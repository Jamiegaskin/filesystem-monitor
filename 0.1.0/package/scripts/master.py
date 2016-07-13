import signal
import sys
import os
from resource_management import *
class Master(Script):
  def install(self, env):
    print 'Install the Sample Srv Master';
  def stop(self, env):
    print 'Stop the Sample Srv Master';
    try:
      print("killing process")
      f = open("/tmp/filesystem.pid", "r")
      os.kill(int(f.read()), signal.SIGTERM)
    except IOError:
      print("pid file non-existent, no process to kill")
    os.unlink("/tmp/filesystem.pid")
  def start(self, env):
    print 'Start the Sample Srv Master';
    call("python /var/lib/ambari-server/resources/common-services/AMSSMOKETESTFAKE/0.1.0/package/scripts/filesystem_monitor.py", wait_for_finish=False, logoutput=True, stdout='/var/log/amssmoketestfake/amssmoketestfake.out', stderr='/var/log/amssmoketestfake/amssmoketestfake.err')
   
  def status(self, env):
    print 'Status of the Sample Srv Master';
    check_process_status("/tmp/filesystem.pid")
  def configure(self, env):
    print 'Configure the Sample Srv Master';
if __name__ == "__main__":
  Master().execute()
