import requests

VERSION = "0.1.0"
WARNING_DEFAULT = 0
CRITICAL_DEFAULT = .5

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
          "widget_name": "{host} Filesystem Status",
          "description": "What percent of filesystems are OK",
          "widget_type": "GAUGE",
          "is_visible": true,
          "metrics": [
            {{
              "name": "{host}.percentOK._avg",
              "metric_path": "metrics/filesystem/{host}.percentOK._avg",
              "service_name": "FILESYSTEM_MONITOR",
              "component_name": "TRANSMITTER"
            }}
          ],
          "values": [
            {{
              "name": "/{host} Percent OK",
              "value": "${{{host}.percentOK._avg}}"
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
                "metrics/filesystem/{0}.percentOK": {{
                  "metric": "{0}.percentOK",
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

GET_URL = "http://{server}:8080/api/v1/clusters/{cluster}/"
FILEPATH = "/var/lib/ambari-server/resources/common-services/FILESYSTEM_MONITOR/{0}/".format(VERSION)


def init_widgets(hosts):
    write_str = WIDGETS_START
    for host in hosts:
        write_str += WIDGETS_TEMPLATE.format(host = host, warning = WARNING_DEFAULT, critical = CRITICAL_DEFAULT)
    #remove last comma
    write_str = write_str[:-1]
    write_str += WIDGETS_END
    with open(FILEPATH + "widgets.json", "w") as ofile:
        ofile.write(write_str)

def init_metrics(hosts):
    write_str = METRICS_START
    write_str += METRICS_TEMPLATE.format('dummy_host', 'dummy_file')
    for host in hosts:
        write_str += METRICS_TEMPLATE.format(host)
    #remove last comma
    write_str = write_str[:-1]
    write_str += METRICS_END
    with open(FILEPATH + "metrics.json", "w") as ofile:
        ofile.write(write_str)

admin_name = raw_input("Admin Username: ")
admin_pass = raw_input("Admin Password: ")
cluster_name = raw_input("Cluster Name: ")
server_host = raw_input("Ambari Server Host Name: ")

cluster_info = requests.get(GET_URL.format(server = server_host, cluster = cluster_name), auth = (admin_name, admin_pass))
hosts = cluster_info.json()['hosts']
hostnames = []
for host in hosts:
    hostnames.append(host['Hosts']['host_name'])
print("Found hosts ", hostnames)
print("Initializing Widgets")
init_widgets(hostnames)
print("Initializing Metrics")
init_metrics(hostnames)
