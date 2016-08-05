import subprocess
import sys
import os
import time
import requests
import socket
import threading
import json

print("Starting up")
"""
ARGS: refresh_interval (seconds), metrics hostname, metrics send port,
        warning threshold, critical threshold
"""
print(sys.argv)
LABELS = ['1K-blocks', 'Used', 'Available', 'Use%', 'Mounted on']
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
JMX_START = """{
  "beans": [ """
JMX_END = """  ]
}
"""
HOST, PORT = '', int(sys.argv[3])
WARNING, CRITICAL = int(sys.argv[4]), int(sys.argv[5])

hostname = open("/etc/hostname", "r").read().strip()


def get_filesystems():
    df = subprocess.Popen(["df", "-P"], stdout=subprocess.PIPE)
    output = df.stdout.read().decode().strip().split("\n")[1:]
    filesystems = {}
    for fs in output:
        fs_arr = fs.split()
        info = {}
        for label, val in zip(LABELS, fs_arr[1:]):
            if label == 'Mounted on':
                info[label] = val
            else:
                info[label] = int(val.replace('%', ''))
        filesystems[fs_arr[0]] = info
    return filesystems

def send_to_metrics(filesystem_name, size_percent):
    #import pdb; pdb.set_trace()
    curr_time = int(time.time() * 1000) #convert to ms
    metric_name = hostname + "_" + filesystem_name
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
    global filesystems
    print("Starting metrics loop")
    while(True):
        filesystems = get_filesystems()
        for name, info in filesystems.iteritems():
            try:
                #print("sending to metrics: ", filename, METRICS_URL)
                send_to_metrics(name, info['Use%'])
            except:
                print("Send to metrics failed", sys.exc_info())
        time.sleep(REFRESH_INTERVAL)

def get_jmx_metrics():
    ok = []
    warning = []
    critical = []
    for name, info in filesystems.iteritems():
        if info['Use%'] > CRITICAL:
            critical.append(name)
        elif info['Use%'] > WARNING:
            warning.append(name)
        else:
            ok.append(name)
    if critical:
        status = 2
    elif warning:
        status = 1
    else:
        status = 0
    return {'status_code': status, 'ok_filesystems': ok,
            'warning_filesystems': warning, 'critical_filesystems': critical}


def metrics_server():
    global filesystems
    print("Starting metrics server")
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((HOST, PORT))
    listen_socket.listen(1)
    while True:
        client_connection, client_address = listen_socket.accept()
        request = client_connection.recv(1024)
        http_response = JMX_START + json.dumps(filesystems[filesystem], sort_keys=True, indent=4) + JMX_END
        print (http_response)
        client_connection.sendall(http_response)
        client_connection.close()

pid = str(os.getpid())
pidfile = "/tmp/filesystem.pid"
file(pidfile, 'w').write(pid)

calc_thread = threading.Thread(target = calc_and_send_metrics)
server_thread = threading.Thread(target = metrics_server)

calc_thread.start()
server_thread.start()
