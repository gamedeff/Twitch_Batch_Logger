"""
This script tracks the changes of user's followed channel and group chat
and store them into cache files for other program to use
"""

import time
import os
import json
import pickle
import configparser
import sys
from urllib.request import urlopen
from copy import deepcopy

# create a folder if one doesn't already exist 
def ensure_dir(dir_path):
    if not os.path.exists(dir_path):
        print("creating directory " + dir_path)
        os.makedirs(dir_path)

def current_time():
	return int(time.time())

def is_event_chat(channel):
	url = "http://api.twitch.tv/api/channels/" + channel + "/chat_properties"
	try:
		info = json.loads(urlopen(url, timeout = 5).read().decode('utf-8'))
		return info["eventchat"]
	except Exception as e:
		print("Exception in is_event_chat: " + str(type(e)) + ": " + str(e), file=sys.stderr)
		return False

def cache_exists(path):
	return os.path.isfile(path)

def load_cache(path):
	with open(path, 'rb') as fp:
	    return pickle.load(fp)

def dump_cache(item, path):
	with open(path, 'wb') as fp:
		pickle.dump(item, fp)

# save the type of channel to local cache
# r for regular chat, e for event chat
# g for group chat, but it's done in group_chat_lookup() below
def update_channel_type_cache(channel_name):
	global channel_type_dict
	channel_type = 'r'
	if is_event_chat(channel_name):
		channel_type = 'e'
	print("channel " + channel_name + " is: " + channel_type)
	channel_type_dict[channel_name] = channel_type
	dump_cache(channel_type_dict, ctd_path)
	time.sleep(0.5)

# add a new channel to the list of followed channels
def followed_channels_list_add(channel_name):
	global followed_channels_list
	if channel_name not in followed_channels_list:
		print("new followed channel: " + channel_name)
		followed_channels_list.append(channel_name)
		dump_cache(followed_channels_list, fcl_path)

# add newly followed channels to local cache
# this stops as soon as all the newly followed channels
# are added, to save time and load on twitch server
def followed_lookup(username):
	# ask twitch for a list of user's followed channels, sorted by most recently followed first
	url = "https://api.twitch.tv/kraken/users/" + username + "/follows/channels?limit=100&sortby=created_at&direction=desc"
	info = json.loads(urlopen(url, timeout = 15).read().decode('utf-8'))
	total_followed = info["_total"]
	while 1:
		for item in info["follows"]:
			# going through the name of followed channels we got from twitch
			# from most recently followed to least recently followed
			channel_name = item['channel']['name'].replace(' ', '').lower()
			# we encounter a channel that's already in the local cache, we know we can
			# stop since the rest will be in cache as well
			if channel_name in followed_channels_list:
				return
			# if a channel is not in local cache, it's newly followed so we add it to local cache
			followed_channels_list_add(channel_name)
			update_channel_type_cache(channel_name)
		next_page = info["_links"]["next"]
		next_offset = int(next_page.split("offset=")[1].split("&")[0])
		if next_offset > total_followed:
			break
		info = json.loads(urlopen(next_page, timeout = 15).read().decode('utf-8'))
		time.sleep(1)

# but how to detect unfollowed channels?
# we do a complete fresh fetch to flush out those unfollowed channels.
def followed_lookup_flush(username):
	global followed_channels_list
	print("doing a fresh fetch")
	current_followed = []
	url = "https://api.twitch.tv/kraken/users/" + username + "/follows/channels?limit=100&sortby=created_at&direction=desc"
	info = json.loads(urlopen(url, timeout = 15).read().decode('utf-8'))
	total_followed = info["_total"]
	while 1:
		for item in info["follows"]:
			channel_name = item['channel']['name'].replace(' ', '').lower()
			if channel_name not in channel_type_dict:
				update_channel_type_cache(channel_name)
			print(channel_name)
			current_followed.append(channel_name)
		next_page = info["_links"]["next"]
		next_offset = int(next_page.split("offset=")[1].split("&")[0])
		if next_offset > total_followed:
			break
		info = json.loads(urlopen(next_page, timeout = 15).read().decode('utf-8'))
		time.sleep(1)
	del followed_channels_list
	followed_channels_list = current_followed
	dump_cache(followed_channels_list, fcl_path)

# get user's group chat so they can be logged as well
def group_chat_lookup():
	global channel_type_dict
	url = "https://chatdepot.twitch.tv/room_memberships?oauth_token=" + oauth.lower().replace("oauth:", '')
	info = json.loads(urlopen(url, timeout = 15).read().decode('utf-8'))
	for item in info["memberships"]:
		is_confirmed = item["is_confirmed"]
		irc_channel = item["room"]["irc_channel"]
		if is_confirmed:
			followed_channels_list_add(irc_channel)
			channel_type_dict[irc_channel] = 'g'

# get an update on followers and group chats
def follow_update(username, flush = False):
	try:
		if flush:
			followed_lookup_flush(username)
		else:
			followed_lookup(username)
		group_chat_lookup()
	except Exception as e:
		print("Exception updating followed channels: " + str(type(e)) + ": " + str(e), file=sys.stderr)
		return

# make sure the two caches are in sync
def cache_coherence_check():
	global channel_type_dict
	global followed_channels_list
	# if the type of a channel is known but it's not followed, remove it
	temp = deepcopy(channel_type_dict)
	for key in temp:
		if key not in followed_channels_list:
			print("removed " + key + " from channel type dict")
			channel_type_dict.pop(key)
	# if a followed channel doesn't have a type, add it to the cache
	for item in followed_channels_list:
		if item not in channel_type_dict:
			update_channel_type_cache(item)
	dump_cache(channel_type_dict, ctd_path)

# read config file
current_directory = os.path.dirname(os.path.abspath(__file__))
config_path = current_directory + "/config.txt"
if os.path.isfile(config_path):
	config = configparser.ConfigParser()
	config.read(config_path)
	oauth = config.get('Settings', 'oauth')
	twitch_username = config.get('Settings', 'username').replace(' ', '').lower()
else:
	print("config.txt not found")
	sys.exit(1)

ensure_dir(current_directory + "/cache")
one_hour = 3600
followed_channels_list = []
fcl_path = current_directory + "/cache/" + twitch_username + "_followed_channels.p"
channel_type_dict = {}
ctd_path = current_directory + "/cache/" + twitch_username + "_channel_type.p"

if cache_exists(fcl_path):
	followed_channels_list = load_cache(fcl_path)
if cache_exists(ctd_path):
	channel_type_dict = load_cache(ctd_path)

cache_coherence_check()
last_flush = current_time()

# update loop
while 1:
	print("\nupdating on " + time.strftime("%Y/%m/%d") + ' ' + time.strftime("%H:%M:%S"))
	# check for unfollowed channels every 4 hours
	if current_time() - last_flush > 4 * one_hour:
		follow_update(twitch_username, flush = True)
		last_flush = current_time()
	else:
		# check for new followed channel every 2 minutes
		follow_update(twitch_username)
	cache_coherence_check()
	time.sleep(120)





