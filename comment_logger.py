import os
import sys
import time
from datetime import datetime
import socket
import irc_bot
import configparser

import pysubs2

def iso8601_utc_now():
	return datetime.utcnow().isoformat(sep='T') + "Z"

def make_offset_str(offset_hours):
	offset_hours = int(offset_hours)
	if offset_hours == 0:
		return "Z"
	if offset_hours > 0:
		sign = "+"
	else:
		sign = "-"
	offset_str = str(abs(offset_hours))
	if len(offset_str) < 2:
		offset_str = "0" + offset_str
	return sign + offset_str + ":00"

def iso8601_local_now():
	return datetime.now().isoformat(sep='T') + make_offset_str(utc_offset_hours)

def parse_chat_server(chat_server):
	return chat_server.replace(' ', '').split(':')

def ensure_dir(dir_path):
    if not os.path.exists(dir_path):
        print("creating directory " + dir_path)
        os.makedirs(dir_path)

def log_add(path, content):
	with open(path, mode='a', encoding='utf-8') as log_file:
		log_file.write(content)

def safe_print(content):
	try:
		print(content)
	except UnicodeEncodeError:
		print(content.encode('utf-8'))

def get_timestamp(ts_format):
	if ts_format == 0:
		return str(time.time())[:15]
	elif ts_format == 2:
		return iso8601_local_now()
	else:
		return iso8601_utc_now()

if(len(sys.argv) != 3):
    print(__file__ + ' channel server_type')
    sys.exit(0)

current_directory = os.path.dirname(os.path.abspath(__file__))
config_path = current_directory + "/config.txt"
if os.path.isfile(config_path):
	config = configparser.ConfigParser()
	config.read(config_path)
	username = config.get('Settings', 'username').replace(' ', '').lower()
	oauth = config.get('Settings', 'oauth')
	record_raw = config.getboolean('Settings', 'record_raw')
	timestamp_format = config.getint('Settings', 'timestamp_format')
	twitchclient_version = config.getint('Settings', 'twitchclient_version')
	regular_chat_server = config.get('Settings', 'regular_chat_server')
	group_chat_server = config.get('Settings', 'group_chat_server')
	event_chat_server = config.get('Settings', 'event_chat_server')
else:
	print("config.txt not found", file=sys.stderr)
	sys.exit(0)

ts = time.time()
utc_offset_hours = int(int((datetime.fromtimestamp(ts) - datetime.utcfromtimestamp(ts)).total_seconds()) / 3600)

server_dict = {'r':parse_chat_server(regular_chat_server), 'g':parse_chat_server(group_chat_server), 'e':parse_chat_server(event_chat_server)}
chat_channel = sys.argv[1]
chat_server = server_dict[sys.argv[2].lower()]

ensure_dir(current_directory + '/comment_log')
if record_raw:
	ensure_dir(current_directory + '/comment_log_raw')

raw_log_path = current_directory + '/comment_log_raw/' + chat_channel + '.txt'
log_path = current_directory + '/comment_log/' + chat_channel + '.txt'

subs_log_path = current_directory + '/comment_log/' + chat_channel + '.ass'

bot = irc_bot.irc_bot(username, oauth, chat_channel, chat_server[0], chat_server[1], twitchclient_version = twitchclient_version)

subs = pysubs2.SSAFile()
i = 0

text = ''

while 1:
	raw_msg_list = bot.get_message()
	if len(raw_msg_list) > 0:
		if len(text) > 0:
			end = pysubs2.time.make_time(ms=datetime.now().microsecond)
			subs.insert(i, pysubs2.SSAEvent(start=start, end=end, text=text.replace('\\', '\\\\')))
			i = i + 1
		start = pysubs2.time.make_time(ms=datetime.now().microsecond)
		text = ''
		timestamp = get_timestamp(timestamp_format)
		for item in raw_msg_list:
			if record_raw:
				log_add(raw_log_path, timestamp + ' ' + item + '\n')
			username, message = irc_bot.parse_user(item)
			if username != '':
				safe_print(chat_channel + " " + username + ": " + message)
				log_add(log_path, timestamp + ' ' + username + ': ' + message + '\n')
				text += username + ": " + message + '\n'
				subs.save(path=subs_log_path, encoding='utf-8')


