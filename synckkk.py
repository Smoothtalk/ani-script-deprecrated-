#!/usr/bin/python

import sys
import os
import linecache
import re
import json
import codecs
import glob
import xml.etree.ElementTree as ET
import multiprocessing
import traceback
from trakt.users import User
from multiprocessing import Process
from collections import OrderedDict

class TvShow():
	title = ""
	last_watched_date = -1
	last_watched_episode = -1
#test
#for automation tools because PATH is hard
# os.chdir(vars.script_loc)

def readJson():
	json_data=open("vars.json").read()
	data = json.loads(json_data, object_pairs_hook=OrderedDict)
	return data #an OrderedDict

def sync(x, settings, User, TvShow, re, traceback, filePath, glob, fileHash):
	allShows = []
	userList = settings['Users'].keys()

	for x in range(len(userList)):
		if(settings['Users'][userList[x]]['traktUserName'] != ""):
			my = User(settings['Users'][userList[x]]['traktUserName'])

			for y in range(len(my.watched_shows)):
				dict = my.watched_shows[y].seasons[-1]

				# gets the episodes (change to -1 to get current season value
				# -2 gets all teh episodes you've watched
				fKey = dict.keys()[-2]
				values = dict[fKey]
				last_episode_watched = values[-1]

				episode_Number =  last_episode_watched['number']
				date_Watched_At = last_episode_watched['last_watched_at']

				traktShow = TvShow();
				traktShow.title = my.watched_shows[y]
				traktShow.last_watched_date = date_Watched_At
				traktShow.last_watched_episode = episode_Number

				dupe = "false"
				for i in allShows:
					if i.title == traktShow.title:
						dupe = "true"
				if dupe == "false":
					allShows.append(traktShow)

				allShows = list(set(allShows))

	#title from torrent
	regex = r"^.*.S\d\d"
	preTitle = re.findall(regex, sys.argv[1], re.IGNORECASE)
	preTitle = str(preTitle)
	preTitle = preTitle[2:-6]
	title = preTitle.replace('.',' ')

	regex = r"S\d\dE\d\d"
	tempSandE = str(re.findall(regex, sys.argv[1], re.IGNORECASE))

	regex = r"\d\d"
	seasonAndEpisodeNumbers = re.findall(regex, tempSandE)

	season = seasonAndEpisodeNumbers[:1]
	episode = seasonAndEpisodeNumbers[1:]

	print "Title: " + title
	print "Season: " + str(season)
	print "Episode: " + str(episode)

	print str(filePath)
	innerFileName = ""

	try:
		os.chdir(filePath)
		for file in glob.glob("*.mkv"):
			innerFileName = file

		for a in allShows:
			if(str(a.title)[9:].lower().split()[:2] == title.lower().split()[:2]):
				filename = title + " - " + 'S' + season[0] + 'E' + episode[0] +".mkv"
				command = "rsync --progress -v -z -e 'ssh -p" + settings['Users']['Smoothtalk']['remote_port'] + "'" + " \"" + filePath + "/" + innerFileName + "\"" + ' ' + "\"" + settings['Users']['Smoothtalk']['remote_host'] + ":" + settings['Users']['Smoothtalk']['remote_download_dir'] + "\""
				os.system(command)
				command = "ssh -p" + settings['Users']['Smoothtalk']['remote_port'] + ' ' + settings['Users']['Smoothtalk']['remote_host'] +  " \"mv '" + settings['Users']['Smoothtalk']['remote_download_dir'] + innerFileName + "' '" + settings['Users']['Smoothtalk']['remote_download_dir'] + filename + "'\""
				os.system(command)
				command = "python3.5 discordAnnounce.py \'" + sys.argv[3] + '\' ' + "0"
				process = subprocess.call(command, shell=True)
				os.chdir(settings['System Settings']['script_location'])
				completed = open("completed.txt", "a")
				completed.write(fileHash)
				completed.write('\n')
				completed.close()
	except:
		sys.exit(1)
		# traceback.print_stack()

settings = readJson()
filePath = settings['System Settings']['host_download_dir'] + sys.argv[1]
hdd = settings['System Settings']['host_download_dir']
fileHash = sys.argv[2]
sync(0, settings, User, TvShow, re, traceback, filePath, glob, fileHash)
