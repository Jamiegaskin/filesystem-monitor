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
cp -R filesystem-monitor/FILESYSTEM_MONITOR /var/lib/ambari-server/resources/stacks/HDP/<HDP_VERSION>/services
cp -R filesystem-monitor/0.1.0 /var/lib/ambari-server/resources/common-services/FILESYSTEM_MONITOR
```

Where HDP_VERSION is your version of HDP (I used 2.4). At this point you should have:
- /var/lib/ambari-server/resources/stacks/HDP/HDP_VERSION/services/FILESYSTEM_MONITOR
- /var/lib/ambari-server/resources/common-services/FILESYSTEM_MONITOR/0.1.0

Go into the filesystem-monitor folder.
```
cd filesystem-monitor
```
Run the script to initialize widgets and metrics.
```
python json_file_generator.py
```
Enter the required info and check to see that the widgets.json and alerts.json file have been created in /var/lib/ambari-server/resources/common-services/FILESYSTEM_MONITOR/0.1.0

Restart Ambari Server.
```
ambari-server restart
```

Installation can now be completed by adding the service "Filesystem Monitor".

*Code adapted from Bryan Bende's tutorials and examples*
