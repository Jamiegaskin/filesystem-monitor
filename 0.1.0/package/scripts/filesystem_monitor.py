import sys
import os
import time
import requests

print("Starting up")
"""
ARGS: refresh_interval (seconds), metrics hostname, files-to-track
"""
print(sys.argv)
REFRESH_INTERVAL = int(sys.argv[1]) #seconds
METRICS_URL = "http://{0}:6188/ws/v1/timeline/metrics".format(sys.argv[2])
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
files = sys.argv[3:]
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

print("Starting metrics loop")

while(True):
    start = time.time()
    clear_memoizer()
    for filename in files:
        size = folder_size_memoize(filename)
        try:
            #print("sending to metrics: ", filename, METRICS_URL)
            send_to_metrics(filename, size)
        except:
            print("exception handling TODO - probably will go to alerts eventually", sys.exc_info())
    end = time.time()
    time.sleep(max(REFRESH_INTERVAL - (end - start), 0))
