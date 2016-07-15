import signal
import sys
import os
from resource_management import *
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
    print 'Stop the Sample Srv Master';
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
    call_list = ["python", "/var/lib/ambari-agent/cache/common-services/filesystem-monitor/0.1.0/package/scripts/filesystem_monitor.py", str(config['check_interval']), config['metrics_host']] + config['folders'].split()
    call(call_list, wait_for_finish=False, logoutput=True, stdout='/var/log/filesystem-monitor/filesystem-monitor.out', stderr='/var/log/filesystem-monitor/filesystem-monitor.err')
   
  def status(self, env):
    check_process_status("/tmp/filesystem.pid")
  def configure(self, env):
    print 'Configure the Filesystem';
    print("New configs: ", Script.get_config()['configurations']['filesystem-config'])
    self.restart()
if __name__ == "__main__":
  Transmitter().execute()
