"""
This script watches user's followed channels and group chats
and spawns / kills comment loggers for each one
"""
import time
import os
import sys
import pickle
import subprocess
import configparser
from copy import deepcopy

# kill the logger process of a channel
def remove_logger(channel):
    global running_logger
    if channel in running_logger:
        print("killing logger for " + channel)
        running_logger[channel].kill()
        running_logger.pop(channel)

# spawn a twitch chat logger for a channel
def add_logger(channel):
    global running_logger
    remove_logger(channel)
    if channel not in running_logger:
        print("adding logger for " + channel)
        logger_path = current_directory + "/comment_logger.py"
        running_logger[channel] = subprocess.Popen([sys.executable,"-u", logger_path, channel, channel_type[channel]], stdout=devnull)
        time.sleep(0.5)

# kill all running loggers then exit
def stop():
    print("killing child processes...", file=sys.stderr)
    temp = deepcopy(running_logger)
    for key in temp:
        remove_logger(key)
    print("killing follow_updater...")
    follow_updater.kill()
    sys.exit(0)

current_directory = os.path.dirname(os.path.abspath(__file__))
config_path = current_directory + "/config.txt"
if os.path.isfile(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    twitch_username = config.get('Settings', 'username').replace(' ', '').lower()
    log_self = config.getboolean('Settings', 'log_self')
else:
    print("config.txt not found")
    sys.exit(1)

fcl_path = current_directory + "/cache/" + twitch_username + "_followed_channels.p"
ctd_path = current_directory + "/cache/" + twitch_username + "_channel_type.p"

followed_channels_prev = set()
channel_type = {}
running_logger = {}
devnull = open(os.devnull, 'w')
follow_updater = subprocess.Popen([sys.executable, "-u", current_directory + "/follow_updater.py"])

try:
    if log_self:
        channel_type[twitch_username] = 'r'
        add_logger(twitch_username)
    while 1:
        # grab an update of followed channels
        try:
            with open(fcl_path, 'rb') as fp:
                followed_list_curr = set(pickle.load(fp))
            with open(ctd_path, 'rb') as fp:
                channel_type = pickle.load(fp)
        except Exception as e:
            print("pickle: " + str(e), file=sys.stderr)
            time.sleep(30)
            continue

        new_followed = followed_list_curr - followed_channels_prev
        unfollowed = followed_channels_prev - followed_list_curr
        followed_channels_prev = followed_list_curr

        # kill the loggers for unfollowed channels
        for item in unfollowed:
            remove_logger(item)

        # spawn loggers for newly followed channels
        for item in new_followed:
            add_logger(item)
            
        time.sleep(30)
        
except KeyboardInterrupt:
    stop()

