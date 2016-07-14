import sys
import os
import time
import requests

REFRESH_INTERVAL = 10 #seconds
METRICS_URL = "http://c6403.ambari.apache.org:6188/ws/v1/timeline/metrics"
METRIC_TEMPLATE = ('{{'
    '"metrics": ['
        '{{'
            '"timestamp": {0},'
            '"metricname": "{1}",'
            '"appid": "filesystem-monitor",'
            '"hostname": "{5}",'
            '"starttime": {2},'
            '"metrics": {{'
                '"{3}": {4}'
                '}}'
            '}}'
        ']'
'}}')
HEADER = {'Content-Type': 'application/json'}
files = ["/home"]
folder_memoizer = {}
status = "RUNNING"
try:
    hostname = open("/etc/hostname", "r").read().strip()
except:
    hostname = "cannot-find-hostname"
    print("cannot find hostname!")

def folder_size_memoize(folder='.'):
    if folder in folder_memoizer:
        return folder_memoizer[folder]
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += folder_size_memoize(itempath)
    return total_size

def clear_memoizer():
    for folder in list(folder_memoizer.keys()):
        if was_modified_within(folder, REFRESH_INTERVAL):
            del folder_memoizer[folder]

def was_modified_within(filename, interval):
    return time.time() - os.path.getmtime(filename) < interval

def send_to_metrics(filename, size):
    #import pdb; pdb.set_trace()
    curr_time = int(time.time() * 1000) #convert to ms
    metric_name = hostname + filename.replace("/", ".")
    json_data = METRIC_TEMPLATE.format(curr_time,
        metric_name, curr_time, curr_time, size,
        hostname)
    post_response = requests.post(METRICS_URL, data = json_data,
        headers = HEADER)
    print("{2} - Name: {0}, Size: {1}, {3}".format(metric_name,
        size, time.ctime(), post_response))
    if post_response.status_code != 200:
        status = "FAILURE"
        print("status not 200!")

pid = str(os.getpid())
pidfile = "/tmp/filesystem.pid"
file(pidfile, 'w').write(pid)
while(True):
    start = time.time()
    clear_memoizer()
    for filename in files:
        size = folder_size_memoize(filename)
        try:
            send_to_metrics(filename, size)
            status = "RUNNING"
        except:
            status = "UNABLE_TO_CONNECT"
            print("exception handling TODO - probably will go to alerts eventually", sys.exc_info()[0])
    end = time.time()
    time.sleep(REFRESH_INTERVAL - (end - start))
