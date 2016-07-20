# filesystem-monitor
Linux filesystem size monitor built for Ambari integration. Ambari service that monitors size of directories on a host machine in a cluster and sends the info to Ambari Metrics.

Built and tested on Centos 6.4 and Ambari 2.2.1 with Python 2.6.6

## Installation
From the ambari server host, get the files.
```
git clone https://github.com/Jamiegaskin/filesystem-monitor
```
If you don't have git, it's as easy as `yum install git` on Centos.

Create a directory for the service.
```
mkdir /var/lib/ambari-server/resources/common-services/FILESYSTEM_MONITOR
```

Copy the files into place.
```
cp -R filesystem-monitor/FILESYSTEM_MONITOR /var/lib/ambari-server/resources/stacks/HDP/HDP_VERSION/services
cp -R filesystem-monitor/0.1.0 /var/lib/ambari-server/resources/common-services/FILESYSTEM_MONITOR
```

Where HDP_VERSION is your version of HDP (I used 2.4). At this point you should have:
- /var/lib/ambari-server/resources/stacks/HDP/HDP_VERSION/services/FILESYSTEM_MONITOR
- /var/lib/ambari-server/resources/common-services/FILESYSTEM_MONITOR/0.1.0

Restart Ambari Server.
```
ambari-server restart
```

Installation can now be completed by adding the service "Filesystem Monitor".

After installation restart the Ambari Server one more time to pick up the auto-configured widgets and metrics.

By default, all hosts are tracking the /home directory. While adding more directories to track is as easy as modifying the configuration and restarting the service, in order to register them as metrics for visuals, you need to edit the metrics.json file at /var/lib/ambari-server/resources/common-services/FILESYSTEM_MONITOR/0.1.0. The naming scheme is HOSTNAME + FILEPATH with all / replaced with . in the filepath (this seemed to help the widgets make the api calls). I've been simply storing the metric at metrics/filesystem/METRIC_NAME. You should be able to copy-paste the /home section and do a simple replace. The Ambari Server will need restarting to pick these changes up. The widgets can be updated manually, but can also be created from the UI.

*Code adapted from Bryan Bende's tutorials and examples*
