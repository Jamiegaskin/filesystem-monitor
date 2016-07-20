import signal
import sys
import os
from resource_management import *

VERSION = "0.1.0"
DEFAULT_MAX_SIZE = 2**30 #1 GB
DEFAULT_FOLDER = 'home'

WIDGETS_START = """{
  "layouts": [
    {
      "layout_name": "default_filesystem_monitor_dashboard",
      "display_name": "Standard FILESYSTEM_MONITOR Dashboard",
      "section_name": "FILESYSTEM_MONITOR_SUMMARY",
      "widgetLayoutInfo": ["""
WIDGETS_END = """
      ]
    }
  ]
}
"""
WIDGETS_TEMPLATE = """
        {{
          "widget_name": "{0} {1} Space Usage",
          "description": "Percentage of available space used in /{1}.",
          "widget_type": "GAUGE",
          "is_visible": true,
          "metrics": [
            {{
              "name": "{0}{1}",
              "metric_path": "metrics/filesystem/{0}{1}._avg",
              "service_name": "FILESYSTEM_MONITOR",
              "component_name": "TRANSMITTER"
            }}
          ],
          "values": [
            {{
              "name": "/{1} Space Utilization",
              "value": "${{{0}{1}}}"
            }}
          ],
          "properties": {{
            "warning_threshold": "0.5",
            "error_threshold": "0.8"
          }}
        }},"""

METRICS_START = """{
  "TRANSMITTER": {
    "Component": [{
        "type": "ganglia",
        "metrics": {
          "default": {"""
METRICS_TEMPLATE = """
                "metrics/filesystem/{0}{1}": {{
                  "metric": "{0}{1}",
                  "pointInTime": true,
                  "temporal": true
                }},"""
METRICS_END = """
          }
        }
    }]
  }
}
"""

FILEPATH = "/var/lib/ambari-server/resources/common-services/FILESYSTEM_MONITOR/{0}/".format(VERSION)

def init_widgets(hosts, files):
    write_str = WIDGETS_START
    for host in hosts:
        for filename in files:
            write_str += WIDGETS_TEMPLATE.format(host, filename)
    #remove last comma
    write_str = write_str[:-1]
    write_str += WIDGETS_END
    with open(FILEPATH + "widgets.json", "w") as ofile:
        ofile.write(write_str)

def init_metrics(hosts, files):
    write_str = METRICS_START
    write_str += METRICS_TEMPLATE.format('dummy_host', 'dummy_file')
    for host in hosts:
        for filename in files:
            write_str += METRICS_TEMPLATE.format(host, filename)
    #remove last comma
    write_str = write_str[:-1]
    write_str += METRICS_END
    with open(FILEPATH + "metrics.json", "w") as ofile:
        ofile.write(write_str)


class Transmitter(Script):
  def install(self, env):
    Execute("yum -y install python-requests.noarch") #putting it as a dependency in the metainfo.xml wasn't working
    if not os.path.exists("/var/log/filesystem-monitor"):
      print("No /var/log/filesystem-monitor - creating")
      try:
        os.makedirs("/var/log/filesystem-monitor")
        print("success creating /var/log/filesystem-monitor")
      except:
        print("creating /var/log/filesystem-monitor failed")

    print("define widgets and metrics if host")
    host = open("/etc/hostname").read().strip()
    all_configs = Script.get_config()
    configs = all_configs['clusterHostInfo']
    folders = all_configs['configurations']['filesystem-config']['folders']
    folders = [x.replace('/', '') for x in folders]
    print("this machine and ambari server host", host, configs['ambari_server_host'])
    if configs['ambari_server_host'][0] == host:
        print("initializing widgets and metrics")
        init_widgets(configs['all_hosts'], folders)
        init_metrics(configs['all_hosts'], folders)

    print("done with custom installation step")
  def stop(self, env):
    try:
      print("killing process")
      f = open("/tmp/filesystem.pid", "r")
      os.kill(int(f.read()), signal.SIGTERM)
      print("process killed")
    except IOError:
      print("pid file non-existent, no process to kill")
    except OSError:
      print("process not running - continuing")
    try:
      os.unlink("/tmp/filesystem.pid")
      print("pid file unlinked")
    except OSError:
      print("no pid file to unlink")
  def start(self, env):
    print 'Start the fileystem monitor';
    self.configure(env) # update metrics
    all_configs = Script.get_config()
    config = all_configs['configurations']['filesystem-config']
    metrics_host = all_configs['clusterHostInfo']['metrics_collector_hosts'][0]
    call_list = ["python", "/var/lib/ambari-agent/cache/common-services/FILESYSTEM_MONITOR/0.1.0/package/scripts/filesystem_monitor.py", str(config['check_interval']), metrics_host] + config['folders'].split() + str(config['folder_sizes']).split()
    call(call_list, wait_for_finish=False, logoutput=True, stdout='/var/log/filesystem-monitor/filesystem-monitor.out', stderr='/var/log/filesystem-monitor/filesystem-monitor.err')

  def status(self, env):
    check_process_status("/tmp/filesystem.pid")
  def configure(self, env):
    all_configs = Script.get_config()
    configs = all_configs['clusterHostInfo']
    folders = all_configs['configurations']['filesystem-config']['folders']
    folders = [x.replace('/', '') for x in folders]
    init_metrics(configs['all_hosts'], folders)

if __name__ == "__main__":
  Transmitter().execute()
