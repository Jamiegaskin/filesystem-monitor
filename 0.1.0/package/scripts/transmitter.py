import signal
import sys
import os
from resource_management import *

VERSION = "0.1.0"
WARNING_DEFAULT = 70
CRITICAL_DEFAULT = 90

FILEPATH = "/var/lib/ambari-server/resources/common-services/FILESYSTEM_MONITOR/{0}/".format(VERSION)

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
    print(all_configs)
    config = all_configs['configurations']['filesystem-config']
    metrics_host = all_configs['clusterHostInfo']['metrics_collector_hosts'][0]
    call_list = ["python",
        "/var/lib/ambari-agent/cache/common-services/FILESYSTEM_MONITOR/0.1.0/package/scripts/filesystem_monitor.py",
        str(config['check_interval']), metrics_host, str(config['port']),
        str(config['threshold_warning']), str(config['threshold_critical'])]
    call(call_list, wait_for_finish=False, logoutput=True,
            stdout='/var/log/filesystem-monitor/filesystem-monitor.out',
            stderr='/var/log/filesystem-monitor/filesystem-monitor.err')

  def status(self, env):
    check_process_status("/tmp/filesystem.pid")
  def configure(self, env):
    return

  def print_configs(self, env):
    print(Script.get_config())


if __name__ == "__main__":
  Transmitter().execute()
