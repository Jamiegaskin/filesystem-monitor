import signal
import sys
import os
from resource_management import *

VERSION = "0.1.0"
WARNING_DEFAULT = 70
CRITICAL_DEFAULT = 90

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
          "description": "Percentage of available space used in {1}.",
          "widget_type": "GAUGE",
          "is_visible": true,
          "metrics": [
            {{
              "name": "{0}{1}._avg",
              "metric_path": "metrics/filesystem/{0}{1}._avg",
              "service_name": "FILESYSTEM_MONITOR",
              "component_name": "TRANSMITTER"
            }}
          ],
          "values": [
            {{
              "name": "/{1} Space Utilization",
              "value": "${{{0}{1}._avg}}"
            }}
          ],
          "properties": {{
            "warning_threshold": "{warning}",
            "error_threshold": "{critical}"
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

ALERTS_START = """{
  "FILESYSTEM_MONITOR": {
    "TRANSMITTER": ["""

ALERTS_TEMPLATE = """
        {{
        "name": "{folder}_size",
        "label": "{folder} disk usage",
        "description": "This alert triggers when a watched folder passes a percentage threshold of its allotted amount",
        "interval": 1,
        "scope": "ANY",
        "enabled": true,
        "source": {{
          "type": "METRIC",
          "uri": {{
            "http": "{{{{filesystem-config/port}}}}",
            "default_port": 6423,
            "connection_timeout": 5.0
          }},
          "reporting": {{
            "ok": {{
              "text": "Usage: {{0:.1%}}"
            }},
            "warning": {{
              "text": "Usage: {{0:.1%}}",
              "value": {warning}
            }},
            "critical": {{
              "text": "Usage: {{0:.1%}}",
              "value": {critical}
            }},
            "units" : "%",
            "type": "PERCENT"
          }},
          "jmx": {{
            "property_list": [
              "Hadoop:name={folder_dots}/{folder_dots}"
            ],
            "value": "{{0}} * 100"
          }}
        }}
      }},"""

ALERTS_END = """
    ]
  }
}
"""

FILEPATH = "/var/lib/ambari-server/resources/common-services/FILESYSTEM_MONITOR/{0}/".format(VERSION)

def init_widgets(hosts, files):
    write_str = WIDGETS_START
    for host in hosts:
        for filename in files:
            write_str += WIDGETS_TEMPLATE.format(host, filename, warning = WARNING_DEFAULT / 100, critical = CRITICAL_DEFAULT / 100)
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

def init_alerts(files):
    write_str = ALERTS_START
    all_configs = Script.get_config()
    server_host = all_configs['clusterHostInfo']['ambari_server_host'][0]
    cluster_name = all_configs['clusterName']
    for filename in files:
        write_str += ALERTS_TEMPLATE.format(folder = filename,
            folder_dots = filename.replace('/', '.'),
            warning = WARNING_DEFAULT,
            critical = CRITICAL_DEFAULT)
    #remove last comma
    write_str = write_str[:-1]
    write_str += ALERTS_END
    with open(FILEPATH + "alerts.json", "w") as ofile:
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
    self.configure(env)
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
    all_configs = Script.get_config()
    config = all_configs['configurations']['filesystem-config']
    metrics_host = all_configs['clusterHostInfo']['metrics_collector_hosts'][0]
    call_list = ["python", "/var/lib/ambari-agent/cache/common-services/FILESYSTEM_MONITOR/0.1.0/package/scripts/filesystem_monitor.py", str(config['check_interval']), metrics_host, str(config['port'])] + config['folders'].split(" ") + str(config['folder_sizes']).split(" ")
    call(call_list, wait_for_finish=False, logoutput=True, stdout='/var/log/filesystem-monitor/filesystem-monitor.out', stderr='/var/log/filesystem-monitor/filesystem-monitor.err')

  def status(self, env):
    check_process_status("/tmp/filesystem.pid")
  def configure(self, env):
    self.update_alerts_metrics(env)

  def print_configs(self, env):
    print(Script.get_config())

  def update_alerts_metrics(self, env):
      all_configs = Script.get_config()
      configs = all_configs['clusterHostInfo']
      folders = all_configs['configurations']['filesystem-config']['folders'].split(" ")
      folders_dots = [x.replace('/', '.') for x in folders]
      host = open("/etc/hostname").read().strip()
      if configs['ambari_server_host'][0] == host:
          print("Initializing Widgets")
          init_widgets(configs['all_hosts'], folders_dots)
          print("Initializing Metrics")
          init_metrics(configs['all_hosts'], folders_dots)
          print("Initializing Alerts")
          init_alerts(folders)

if __name__ == "__main__":
  Transmitter().execute()
