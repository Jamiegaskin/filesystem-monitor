import signal
import sys
import os
from resource_management import *

VERSION = "0.1.0"
DEFAULT_MAX_SIZE = 2**30 #1 GB

WIDGETS_START = """{
  "layouts": [
    {
      "layout_name": "default_filesystem_monitor_dashboard",
      "display_name": "Standard FILESYSTEM_MONITOR Dashboard",
      "section_name": "FILESYSTEM_MONITOR_SUMMARY",
      "widgetLayoutInfo": [
            """
WIDGETS_END = """      ]
    }
  ]
}
"""
WIDGETS_TEMPLATE = """{
          "widget_name": "{0} /{1} Space Usage",
          "description": "Percentage of available space used in /{1}.",
          "widget_type": "GAUGE",
          "is_visible": true,
          "metrics": [
            {
              "name": "{0}.ambari.apache.org.{1}",
              "metric_path": "metrics/filesystem/{0}.ambari.apache.org.{1}",
              "service_name": "FILESYSTEM_MONITOR",
              "component_name": "TRANSMITTER"
            }
          ],
          "values": [
            {
              "name": "/{1} Space Utilization",
              "value": "${{{0}.ambari.apache.org.{1}/{2}}}"
            }
          ],
          "properties": {
            "warning_threshold": "0.5",
            "error_threshold": "0.8"
          }
        },
"""

METRICS_START = """{
  "TRANSMITTER": {
    "Component": [{
        "type": "ganglia",
        "metrics": {
          "default": {
                """
METRICS_TEMPLATE = """"metrics/{0}.ambari.apache.org.{1}": {
  "metric": "{0}.ambari.apache.org.{1}",
  "pointInTime": true,
  "temporal": true
},
"""
METRICS_END = """          }
        }
    }]
  }
}
"""

FILEPATH = "/var/lib/ambari-server/resources/common-services/FILESYSTEM_MONITOR/{0}/".format(VERSION)

def init_widgets(hosts, file_name, size):
    write_str = WIDGETS_START
    for host in hosts:
        write_str += WIDGETS_TEMPLATE.format(host, file_name, size)
    #remove last comma
    write_str = write_str[:-1]
    write_str += WIDGETS_END
    with open(FILEPATH + "widgets.json", "w") as ofile:
        ofile.write(write_str)

def init_metrics(hosts, file_name):
    write_str = METRICS_START
    for host in hosts:
        write_str += METRICS_TEMPLATE.format(host, file_name)
    #remove last comma
    write_str = write_str[:-1]
    write_str += METRICS_END
    with open(FILEPATH + "metrics.json", "w") as ofile:
        ofile.write(write_str)


class Transmitter(Script):
  def install(self, env):
    Execute("yum -y install python-requests.noarch") #putting it as a dependency in the metainfo.xml wasn't working
    print("Host: ", open("/etc/hostname").read())
    if not os.path.exists("/var/log/filesystem-monitor"):
      print("No /var/log/filesystem-monitor - creating")
      try:
        os.makedirs("/var/log/filesystem-monitor")
        print("success creating /var/log/filesystem-monitor")
      except:
        print("creating /var/log/filesystem-monitor failed")
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
    #self.configure(env) # for safety
    config = Script.get_config()['configurations']['filesystem-config']
    call_list = ["python", "/var/lib/ambari-agent/cache/common-services/FILESYSTEM_MONITOR/0.1.0/package/scripts/filesystem_monitor.py", str(config['check_interval']), config['metrics_host']] + config['folders'].split()
    call(call_list, wait_for_finish=False, logoutput=True, stdout='/var/log/filesystem-monitor/filesystem-monitor.out', stderr='/var/log/filesystem-monitor/filesystem-monitor.err')

  def status(self, env):
    check_process_status("/tmp/filesystem.pid")
  def configure(self, env):
    print 'Configure the Filesystem';
    print("New configs: ", Script.get_config()['configurations']['filesystem-config'])
    self.restart()
if __name__ == "__main__":
  Transmitter().execute()
