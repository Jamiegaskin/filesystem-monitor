# filesystem-monitor
Linux filesystem size monitor built for Ambari integration. Ambari service that monitors size of directories on a host machine in a cluster and sends the info to Ambari Metrics.

Built and tested on Centos 6.4 and Ambari 2.2.1 with Python 2.6.6

## Installation
From the ambari server host, get the files.
```
git clone https://github.com/Jamiegaskin/filesystem-monitor
```
If you don't have git, it's as easy as `yum install git` on Centos

Create the directories.
```
mkdir /var/lib/ambari-server/resources/stacks/HDP/HDP_VERSION/services/FILESYSTEM_MONITOR
mkdir /var/lib/ambari-server/resources/common-services/FILESYSTEM_MONITOR
```
Where HDP_VERSION is your version of HDP (I used 2.4).

Move the files into place.
```
mv filesystem-monitor/metainfo.xml /var/lib/ambari-server/resources/stacks/HDP/HDP_VERSION/services/FILESYSTEM_MONITOR/metainfo.xml
mv filesystem-monitor/0.1.0 /var/lib/ambari-server/resources/common-services/filesystem-monitor/0.1.0
```

Restart Ambari Server.
```
ambari-server restart
```

Installation can now be completed by adding the service "Filesystem Monitor". The only configuration you **must** set immediately is the host name for the Ambari Metrics Collector.

## Known issues
- Start/stop from the UI don't function. Can start or stop individual components or all by using the Ambari API.

Stop:
``` 
curl -u ADMIN_USER:ADMIN_PASSWORD -H "X-Requested-By: ambari" -X PUT -d '{"RequestInfo":{"context":"Stop Service"},"Body":{"ServiceInfo":{"state":"INSTALLED"}}}' http://AMBARI_SERVER:8080/api/v1/clusters/CLUSTER_NAME/services/FILESYSTEM_MONITOR
```
Start:
``` 
curl -u ADMIN_USER:ADMIN_PASSWORD -H "X-Requested-By: ambari" -X PUT -d '{"RequestInfo":{"context":"Start Service"},"Body":{"ServiceInfo":{"state":"STARTED"}}}' http://AMBARI_SERVER:8080/api/v1/clusters/CLUSTER_NAME/services/FILESYSTEM_MONITOR
```
- Widgets view still being worked on
*Code adapted from Bryan Bende's tutorials and examples*
