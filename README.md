# filesystem-monitor
Linux filesystem size monitor built for Ambari integration. Ambari service that monitors size of filesystems on a host machine in a cluster and sends the info to Ambari Metrics.

Built and tested on Centos 6.4 and Ambari 2.2.1 with Python 2.6.6

## Installation
The setup here requires the "requests" module for Python.
```
yum install python-requests.noarch
```
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

## Known Issues:
- Widgets must be modified from the web UI after initialization. The widgets.json file doesn't do anything after the service is installed.
- Similarly with alerts, they must be modified from the UI or the alerts API
- Sometimes not all metrics in the metrics.json file show up in the web UI. Sometimes inserting a dummy metric at the start or end will solve this problem, but not always.
- If you are having trouble installing python-requests due to file conflicts, running `yum clean all` then `yum update` often fixes the issue.

*Code adapted from Bryan Bende's tutorials and examples*
