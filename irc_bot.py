import os
import sys
import time
import socket

def parse_user(raw_msg):
	if 'PRIVMSG' in raw_msg and raw_msg.count(":") > 1:
		username = raw_msg.split(' ', 1)[0].split('!')[0].replace(':', '').lower()
		comment = raw_msg.split(' :')[-1]
		if username != 'jtv' and 'tmi.' not in username:
			return username, comment
	return '', ''

class irc_bot(object):
	def __init__(self, nickname, oauth, channel, host, port, timeout = 600, twitchclient_version = 3):
		self.NICK = nickname
		self.AUTH = oauth
		self.CHAT_CHANNEL = channel
		self.HOST = host
		self.PORT = int(port)
		self.sock = socket.socket()
		self.timeout = timeout
		self.tc_version = int(twitchclient_version)
		self.is_connected = False

	def connect(self):
		del self.sock
		self.sock = socket.socket()
		self.sock.settimeout(5)
		self.sock.connect((self.HOST, self.PORT))
		self.sock.send(bytes("PASS %s\r\n" % self.AUTH, "UTF-8"))
		self.sock.send(bytes("NICK %s\r\n" % self.NICK, "UTF-8"))
		self.sock.send(bytes("USER %s %s bla :%s\r\n" % (self.NICK, self.HOST, self.NICK), "UTF-8"))
		self.sock.send(bytes("JOIN #%s\r\n" % self.CHAT_CHANNEL, "UTF-8"));
		print(self.NICK + ": connected to " + self.CHAT_CHANNEL)
		if self.tc_version > 0:
			tc_message = "TWITCHCLIENT " + str(self.tc_version) + "\r\n"
			self.sock.send(bytes(tc_message, "UTF-8"))
		self.sock.settimeout(self.timeout)
		self.is_connected = True

	def update(self):
		if not self.is_connected:
			self.retry_connect()
		recv_buffer = []
		raw_msg_list = self.sock.recv(1024).decode("UTF-8", errors = "ignore").split("\n")
		for item in [s for s in raw_msg_list if len(s) > 0]:
			item = item.replace('\r', '')
			if "PRIVMSG" not in item and 'tmi.twitch.tv' in item and 'PING' in item:
				self.sock.send(bytes("PONG tmi.twitch.tv\r\n", "UTF-8"))
			if "PRIVMSG" not in item and "tmi.twitch.tv" in item and "Login unsuccessful" in item:
				print(self.NICK + ": Login failed! check your username and oauth", file=sys.stderr)
				sys.exit(1)
			recv_buffer.insert(0, item)
		return recv_buffer

	def retry_connect(self):
		while 1:
			time.sleep(0.5)
			try:
				self.connect()
			except Exception as e:
				print("Exception while trying to connect: " + str(type(e)) + ": " + str(e), file=sys.stderr)
				time.sleep(2)
				continue
			break

	def get_message(self):
		while 1:
			try:
				return self.update()
			except Exception as e:
				print("Exception receiving messages: " + str(type(e)) + ": " + str(e), file=sys.stderr)
				self.retry_connect()

	def get_user_message(self):
		ret = []
		for item in self.get_message():
			username, comment = parse_user(item)
			if username != '':
				ret.append((username, comment))
		return ret

	def send_message(self, message):
		try:
			self.sock.send(bytes("PRIVMSG #%s :%s\r\n" % (self.CHAT_CHANNEL, message), "UTF-8"))
		except Exception as e:
			print("Exception sending message: " + str(type(e)) + ": " + str(e), file=sys.stderr)
			self.retry_connect()