import sys
from resource_management import *
class Master(Script):
  def install(self, env):
    print 'Install the Filesystem Master';
    self.install_packages(env)
  def stop(self, env):
    print 'Stop the Filesystem Master';
  def start(self, env):
    print 'Start the Filesystem Master';

  def status(self, env):
    print 'Status of the Filesystem Master';
  def configure(self, env):
    print 'Configure the Filesystem Master';
  def service_check(self, env):
    print 'Service check the Filesystem';
if __name__ == "__main__":
  Master().execute()
