#!/usr/bin/env python

import collections
import os
from resource_management.libraries.script import Script
import requests
from time import time
import sys

DiskInfo = collections.namedtuple('DiskInfo', 'percent path')

# script parameter keys
PERCENT_USED_WARNING_KEY = "warning_threshold"
PERCENT_USED_CRITICAL_KEY = "critical_threshold"

# defaults in case no script parameters are passed
MIN_FREE_SPACE_DEFAULT = 5000000000L
PERCENT_USED_WARNING_DEFAULT = 70
PERCENT_USED_CRITICAL_DEFAULT = 90

config = Script.get_config()
cluster_name = config['Clusters']['cluster_name']
ambari_server = config['clusterHostInfo']['ambari_server_host'][0]

URL_GET_TEMPLATE = "http://{ambari_server}:8080/api/v1/clusters/{cluster_name}/services/FILESYSTEM_MONITOR/components/TRANSMITTER?fields=metrics/filesystem/{metric}&_={curr_time}"


def execute(configurations={}, parameters={}, host_name=None):
  """
  Keyword arguments:
  configurations (dictionary): a mapping of configuration key to value
  parameters (dictionary): a mapping of script parameter key to value
  host_name (string): the name of this host where the alert is running
  """
  path = parameters['filepath']
  disk_usage = get_folder_percent(path, host_name)
  result_code, label = _get_warnings_for_partition(parameters, disk_usage)
  return result_code, [label]


def _get_warnings_for_partition(parameters, disk_usage):

  # start with hard coded defaults
  warning_percent = PERCENT_USED_WARNING_DEFAULT
  critical_percent = PERCENT_USED_CRITICAL_DEFAULT

  if PERCENT_USED_WARNING_KEY in parameters:
    warning_percent = float(parameters[PERCENT_USED_WARNING_KEY])

  if PERCENT_USED_CRITICAL_KEY in parameters:
    critical_percent = float(parameters[PERCENT_USED_CRITICAL_KEY])


  if disk_usage is None:
    return 'UNKNOWN', ['Unable to determine the disk usage']

  result_code = 'OK'
  percent = disk_usage.percent * 100
  if percent > critical_percent:
    result_code = 'CRITICAL'
  elif percent > warning_percent:
    result_code = 'WARNING'

  label = 'Capacity Used: {0:.2f}%'.format(percent)

  if disk_usage.path is not None:
    label += ", path=" + disk_usage.path

  return result_code, label

def get_folder_percent(path='/', hostname = ""):
  """
  returns a named tuple that contains the total, used folder space
  in percent. Linux implementation.
  """
  used = 0
  total = 0
  free = 0

  metric_name = hostname + path.replace("/", ".")
  try:
      folder_percent_call = requests.get(URL_GET_TEMPLATE.format(ambari_server = ambari_server, cluster_name = cluster_name, metric = metric_name, curr_time = int(time() * 1000)))
  except:
      print("API error", sys.exc_info())
      return None
  if folder_percent_call.status_code != 200:
      print("status code not 200", folder_percent_call.status_code)
      return None

  return DiskInfo(percent = folder_percent_call.json()['metrics']['filesystem'][metric_name], path=path)
