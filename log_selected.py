import os
import sys
import time
import json
import subprocess
from urllib.request import urlopen
from urllib.error import HTTPError
from copy import deepcopy

def channel_type_check(channel):
    time.sleep(0.5)
    url = "http://api.twitch.tv/api/channels/" + channel + "/chat_properties"
    try:
        info = json.loads(urlopen(url, timeout = 5).read().decode('utf-8'))
        if info["eventchat"]:
            return "e"
        else:
            return "r"
    except HTTPError as e:
        if e.code == 404 and is_group_chat(channel):
            return "g"
    return ""

def read_channels():
    file_path = current_directory + "/recorded_channels.txt"
    if not os.path.isfile(file_path):
        print("no channel list file found")
        sys.exit(0)
    channel_list = []
    with open(file_path) as channel_list_file:
        while 1:
            this_line = channel_list_file.readline()
            this_line = this_line.replace(' ', '').lower()
            if this_line == '':
                break
            if this_line[0] == ";":
                continue
            this_line = this_line.replace('\n', '')
            if len(this_line) > 0:
                channel_list.append(this_line)
    return channel_list

def is_group_chat(name):
    return len(name) > 0 and name[0] == "_" and name.count("_") >= 2 and name[-13:].isnumeric()

# kill the logger process of a channel
def remove_logger(channel):
    global running_logger
    if channel in running_logger:
        print("killing logger for " + channel)
        running_logger[channel].kill()
        running_logger.pop(channel)

# spawn a twitch chat logger for a channel
def add_logger(channel, channel_type):
    global running_logger
    remove_logger(channel)
    if channel not in running_logger:
        print("spawning logger for " + channel)
        logger_path = current_directory + "/comment_logger.py"
        running_logger[channel] = subprocess.Popen([sys.executable, "-u", logger_path, channel, channel_type], stdout=devnull)
        time.sleep(0.5)

# kill all running loggers then exit
def stop():
    print("killing child processes...", file=sys.stderr)
    temp = deepcopy(running_logger)
    for key in temp:
        remove_logger(key)
    sys.exit(0)

current_directory = os.path.dirname(os.path.abspath(__file__))
channel_list = read_channels()
channel_type_dict = {}
running_logger = {}
devnull = open(os.devnull, 'w')

print("\nverifying channels")
for item in channel_list:
    print(item + " ", end = "")
    channel_type = channel_type_check(item)
    if channel_type == "":
        print(" doesn't exist, skipped")
        continue
    print("...ok")
    channel_type_dict[item] = channel_type
print()

try:
	for key in channel_type_dict:
	    add_logger(key, channel_type_dict[key])
	while 1:
	    time.sleep(60)
except KeyboardInterrupt:
	stop()








