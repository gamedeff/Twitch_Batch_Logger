A lightweight Twitch chat logger that logs all channels and group chats you follow on Twitch, or just a select few from a list that you provide.

# Features

* Log all your followed Twitch channels and group chats

* Or just log from a list of channels that you provide

* Automatically select chat server (regular, event, group)

* Option to log chat metadata (user color, sub notification, mod events, etc.)

* Configurable timestamp formats

* Low CPU and memory usage

* Tested on Windows 7 64-bit, OS X Yosemite, and Raspbian on Raspberry Pi

# Requirements

Only Python 3.2+ is needed.

Download and install the latest version at https://www.python.org/downloads/

Raspbian on Raspberry Pi already has Python 3.2 so it should work out of the box.

# How To Use

## 1. Setting up your configure file

* Open config.txt in your favorite text editor

* Add your own twitch username and oauth. You can get your oauth at http://twitchapps.com/tmi/

![alt tag](http://i.imgur.com/467b7sb.png)

* Take a look at other settings and change them if you want.

![alt tag](http://i.imgur.com/o76oDfk.png)

## 2. Start logging

### Log all channels and group chats you follow on Twitch

Type 
` python3 log_all.py