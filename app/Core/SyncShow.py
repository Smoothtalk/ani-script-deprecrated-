#!/usr/bin/python

import sys
import os
import re
import json
import glob
import traceback
import subprocess
from trakt.users import User
from fuzzywuzzy import fuzz
from collections import OrderedDict

FUZZ_RATIO = 70

class TvShow:
	def __init__(self, title, lwd, lwe):
		self.title = title
		self.last_watched_date = lwd
		self.last_watched_episode = lwe

	def getTitle(self):
		return self.title
	def getLast_watched_date(self):
		return self.last_watched_date
	def getlast_watched_episode(self):
		return self.last_watched_episode

class SyncUser:
	def __init__(self, user, userSettings):
		self.userName = user
		self.remote_port = userSettings['remote_port']
		self.remote_host = userSettings['remote_host']
		self.remote_download_dir = userSettings['remote_download_dir']
		self.local_download_dir = userSettings['local_download_dir']
		self.discord_ID = userSettings['discord_ID']
		self.traktUserName = userSettings['traktUserName']
		self.custom_titles = userSettings['custom_titles']
		self.shows = [] #titles of show

	def getUserName(self):
		return self.userName
	def getRemote_Port(self):
		return self.remote_port
	def getRemote_Host(self):
		return self.remote_host
	def getRemote_Download_Dir(self):
		return self.remote_download_dir
	def getLocal_Download_Dir(self):
		return self.local_download_dir
	def getDiscord_ID(self):
		return self.discord_ID
	def getTraktUserName(self):
		return self.traktUserName
	def getCustom_Titles(self):
		return self.custom_titles
	def addShow(self, show):
	 	self.shows.append(show)
	def getShows(self):
		return self.shows

class Release:
	def __init__(self, inputVar):
		#title from torrent
		regex = r"^.*.S\d\d"
		preTitle = re.findall(regex, inputVar, re.IGNORECASE)
		preTitle = str(preTitle)
		preTitle = preTitle[2:-6]

		regex = r"S\d\dE\d\d"
		tempSandE = str(re.findall(regex, inputVar, re.IGNORECASE))

		regex = r"\d\d"
		seasonAndEpisodeNumbers = re.findall(regex, tempSandE)

		self.title = preTitle.replace('.',' ')
		self.season = seasonAndEpisodeNumbers[:1]
		self.episode = seasonAndEpisodeNumbers[1:]

	def getTitle(self):
		return self.title
	def getSeason(self):
		return self.season[0]
	def getEpisode(self):
		return self.episode[0]

def readJson():
	json_data=open("vars.json").read()
	data = json.loads(json_data, object_pairs_hook=OrderedDict)
	return data #an OrderedDict

def getTraktShows(syncUser):
	my = User(syncUser.getTraktUserName())

	for y in range(len(my.watched_shows)):
		theDict = my.watched_shows[y].seasons[-1]

		# # gets the episodes (change to -1 to get current season value
		# # -2 gets all teh episodes you've watched
		fKey = list(theDict.keys())[-2]
		#dictionaries change the first value on a whim, sometimes its episodes sometimes its numbers
		if(fKey == "number"):
			fKey = list(theDict.keys())[-1]
		values = theDict[fKey]
		last_episode_watched = values[-1]

		episode_Number =  last_episode_watched['number']
		date_Watched_At = last_episode_watched['last_watched_at']

		traktShow = TvShow(my.watched_shows[y].title, date_Watched_At, episode_Number);

		syncUser.addShow(traktShow)

def match(release, traktShows):
	match = None
	for show in traktShows:
		# print release.getTitle()
		if (fuzz.ratio(show.getTitle(), release.getTitle()) > FUZZ_RATIO):
			match = show
	return match

def sync(settings, syncingUser, match, glob, filePath):
	innerFileName = ""

	try:
		os.chdir(filePath)
		for file in glob.glob("*.mkv"):
			innerFileName = file
			filename = match.getTitle() + " - " + 'S' + match.getSeason() + 'E' + match.getEpisode() + ".mkv"

			if(syncingUser.getRemote_Host() != ''):
				if(settings['System Settings']['individual folders'] == "True"):
					seriesFolder = (match.getTitle() + '/' + "Season " + match.getSeason())
					command = "ssh -p" + syncingUser.getRemote_Port() + ' ' + syncingUser.getRemote_Host() + " \"mkdir -p " + syncingUser.getRemote_Download_Dir() + seriesFolder.replace(" ", "\ ") + '"'
					os.system(command)
					command = "rsync --progress -v -z -e 'ssh -p" + syncingUser.getRemote_Port() + "'" + " \"" + filePath + "/" + innerFileName + "\"" + ' ' + "\"" + syncingUser.getRemote_Host() + ":" + syncingUser.getRemote_Download_Dir() + seriesFolder.replace(" ", "\ ") + "\""
					os.system(command)
					command = "ssh -p" + syncingUser.getRemote_Port() + ' ' + syncingUser.getRemote_Host() + " \"mv '" + syncingUser.getRemote_Download_Dir() + seriesFolder + '/' + innerFileName + "' '" + syncingUser.getRemote_Download_Dir() + seriesFolder + '/' + filename + "'\""
					os.system(command)
				elif(settings['System Settings']['individual folders'] == "False"):
					command = "rsync --progress -v -z -e 'ssh -p" + syncingUser.getRemote_Port() + "'" + " \"" + filePath + "/" + innerFileName + "\"" + ' ' + "\"" + syncingUser.getRemote_Host() + ":" + syncingUser.getRemote_Download_Dir() + "\""
					os.system(command)
					command = "ssh -p" + syncingUser.getRemote_Port() + ' ' + syncingUser.getRemote_Host() +  " \"mv '" + syncingUser.getRemote_Download_Dir() + '/' + innerFileName + "' '" + syncingUser.getRemote_Download_Dir() + '/' + filename + "'\""
					os.system(command)
			else: #want to keep it on server
				if(syncingUser.getLocal_Download_Dir() != ''):
					command = "cp \'" + filePath + "/" + innerFileName + "\' \'" + syncingUser.getLocal_Download_Dir() + filename + "\'"
					print (command)
					#os.system(command)
					#copy file to download dir

		os.chdir(settings['System Settings']['script_location'])
		command = "python3.5 Tools/DiscordAnnounce.py \'" + filename + '\' ' + syncingUser.getUserName()
		process = subprocess.call(command, shell=True)

	except Exception as e:
			print (e)
			traceback.print_stack()


settings = readJson()
filePath = sys.argv[1]
syncRelease = Release(sys.argv[2])

os.chdir(settings['System Settings']['script_location'])

for user in settings['Users']:
	if (settings['Users'][user]['traktUserName'] != ""):
		syncingUser = SyncUser(user, settings['Users'][user])
		getTraktShows(syncingUser)
		match = match(syncRelease, syncingUser.getShows())
		if (match is not None):
			print ("Syncing: " + str(match.getTitle()))
			sync(settings, syncingUser, syncRelease, glob, filePath)
