A lightweight Twitch chat logger that logs all channels and group chats you follow on Twitch, or just a select few from a list that you provide.

# Features

* Log all your followed Twitch channels and group chats

* Or just log from a list of channels that you specify

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

## 1. Set up your configuration file

* Open config.txt in your favorite text editor

* Add your own twitch username and oauth. You can get your oauth at http://twitchapps.com/tmi/

![alt tag](http://i.imgur.com/467b7sb.png)

* Take a look at other settings and change them if you want.

![alt tag](http://i.imgur.com/o76oDfk.png)

## 2. Start logging


**Warning: Do not use Cygwin for this program in Windows. It doesn't pass keyboard interrupt correctly and will cause this program to terminate without killing its spawned loggers. Use the built-in cmd.exe instead.**


### Option 1: Log all channels and group chats you follow on Twitch

Run `python3 log_all.py` in your terminal.

The program will search for all your followed channels and group chats you're in and add loggers for each of them. It might take a while depending on the number of channels you follow.

It will also add/remove loggers automatically as you follow/unfollow channels on Twitch.

![alt tag](http://i.imgur.com/Z3jmhEC.png)

Once logging starts you should see the text files of your followed channels in ./comment_log folder

![alt tag](http://i.imgur.com/GLzM6nk.png)

Inside of which are your intellectual and informative twitch chat logs

![alt tag](http://i.imgur.com/GGHD6O6.png)

To stop the program press Control + C.

### Option 2: Only log channels from a list you provide.

Open recorded_channels.txt and add channels you wish to log, one channel per line.

![alt tag](http://i.imgur.com/vzkTpgQ.png)

Run `python3 log_selected.py` in your terminal.

The program will verify each channel to make sure it exists and determine its type, then launch chat logger for each of them.

![alt tag](http://i.imgur.com/GVF9u7M.png)

The rest is the same with Option 1

# Resource Usage

This program should consume minimum amount of memory and CPU while running.

While logging 82 channels on Raspberry Pi 2 with 1GB memory and 900MHz ARM Cortex-A7 CPU, the program uses around 4.5MB of memory per logger and almost no CPU usage at all, with load average below 0.05

The resource impact should be even less when running on a full-sized PC.

![alt tag](http://i.imgur.com/c1lN5uJ.png)

I do recommend using a Raspberry Pi 2 as a logging machine and let the program run 24/7, this way you have a complete log of twitch chat, and avoid the cost of running a full-sized PC.