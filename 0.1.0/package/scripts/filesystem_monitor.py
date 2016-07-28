import sys
import os
import time
import requests
import socket

print("Starting up")
"""
ARGS: refresh_interval (seconds), metrics hostname, metrics send port, files-to-track, file-sizes
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
JMX_START = """{{
  "beans": [ """
JMX_END = """  ]
}
"""
HOST, PORT = '', sys.argv[3]

file_info = sys.argv[4:]
num_files = len(file_info) / 2
file_names = file_info[:num_files]
file_max_sizes = [float(x) for x in file_info[num_files:]]
files = dict(zip(file_names, file_max_sizes))
folder_memoizer = {}
file_sizes = {}

hostname = open("/etc/hostname", "r").read().strip()

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

def send_to_metrics(filename, size, maxsize):
    #import pdb; pdb.set_trace()
    curr_time = int(time.time() * 1000) #convert to ms
    metric_name = hostname + filename
    size_percent = size / maxsize
    json_data = METRIC_TEMPLATE.format(curr_time,
        metric_name, curr_time, curr_time, size_percent,
        hostname)
    post_response = requests.post(METRICS_URL, data = json_data,
        headers = HEADER)
    print("{2} - Name: {0}, Size: {1}%, {3}".format(metric_name,
        size_percent, time.ctime(), post_response))
    if post_response.status_code != 200:
        status = "FAILURE"
        print("status not 200!")

def calc_and_send_metrics():
    global file_sizes
    print("Starting metrics loop")
    while(True):
        start = time.time()
        clear_memoizer()
        for filename, maxsize in files.iteritems():
            size = folder_size_memoize(filename)
            filename_dots = filename.replace('/', '.')
            file_sizes[filename_dots] = size
            try:
                #print("sending to metrics: ", filename, METRICS_URL)
                send_to_metrics(filename_dots, size, maxsize)
            except:
                print("Send to metrics failed", sys.exc_info())
        end = time.time()
        time.sleep(max(REFRESH_INTERVAL - (end - start), 0))

def metrics_server():
    global file_sizes
    print("Starting metrics server")
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((HOST, PORT))
    listen_socket.listen(1)
    while True:
        client_connection, client_address = listen_socket.accept()
        request = client_connection.recv(1024)
        print (request)
        http_response = JMX_START + json.dumps(file_sizes, sort_keys=True, indent=4) + JMX_END
        client_connection.sendall(http_response)
        client_connection.close()

pid = str(os.getpid())
pidfile = "/tmp/filesystem.pid"
file(pidfile, 'w').write(pid)

calc_thread = threading.Thread(target = calc_and_send_metrics)
server_thread = threading.Thread(target = metrics_server)

calc_thread.start()
server_thread.start()
