#!/usr/bin/python

import sys
import os
import json
import subprocess
import xml.etree.ElementTree as ET
import multiprocessing
from fuzzywuzzy import fuzz
from multiprocessing import Process
from collections import OrderedDict

FUZZ_RATIO = 70

class Series:
	seriesName = ""
	episode = None
	fileName = ""
	filePath = ""

	def getSeriesName(self):
		return self.seriesName
	def getSeriesEpisode(self):
		return self.episode
	def setSeriesTitle(self, fileName):
		tempName = fileName.replace("_", " ")
		firstHyphen = tempName.rfind(' - ')
		firstCBrac = tempName.index(']', 0)
		seriesName = tempName[firstCBrac+2:firstHyphen]
		episode = tempName[firstHyphen+3:]
		episode = episode[:episode.index(' ',0)]
		filename = seriesName + ' - ' + episode + '.mkv'

		seriesName = seriesName.strip()

		self.seriesName = seriesName
		self.episode = episode
		self.fileName = filename
	def getFileName(self):
		return self.fileName
	def setFilePath(self, filePath):
		self.filePath = filePath
	def getFilePath(self):
		return self.filePath

class User:
	def __init__(self, user, userSettings):
		self.userName = user
		self.remote_port = userSettings['remote_port']
		self.remote_host = userSettings['remote_host']
		self.remote_download_dir = userSettings['remote_download_dir']
		self.discord_ID = userSettings['discord_ID']
		self.custom_titles = userSettings['custom_titles']
		self.MalShows = {} #titles of mal shows
		self.malDatabaseFileName = "Data/" + user + ".xml" #Database File name

	def getUserName(self):
		return self.userName
	def getRemote_Port(self):
		return self.remote_port
	def getRemote_Host(self):
		return self.remote_host
	def getRemote_Download_Dir(self):
		return self.remote_download_dir
	def getDiscord_ID(self):
		return self.discord_ID
	def getCustom_Titles(self):
		return self.custom_titles
	def addMalShow(self, malShow, episodesWatched):
		newShow = {malShow: {'episodesWatched': episodesWatched}}
		self.MalShows.update(newShow)
	def getMalShows(self):
		return self.MalShows
	def getMalDatabaseFileName(self):
		return self.malDatabaseFileName

def readJson():
	json_data=open("vars.json").read()
	data = json.loads(json_data, object_pairs_hook=OrderedDict)
	return data #an OrderedDict

def pullMALUserData(userList):
	for user in userList:
		command = "python3.5 Tools/retMal.py " + '\"' + user + '\"'
		os.system(command)

def getMALShows(malUserFile, user):
	with open(malUserFile, 'rt') as f:
		tree = ET.parse(f)

		for node in tree.findall('.//anime'):
			raw_status = node.find('my_status').text
			status = raw_status.strip()
			if status == '1' or status == '6':
				raw_title = node.find('series_title').text
				raw_alt_title = node.find('series_synonyms').text #this is a list
				raw_my_watched_episodes = node.find('my_watched_episodes').text

				title = raw_title.strip()
				alt_title_unsplit = raw_alt_title.strip()
				alt_title = alt_title_unsplit.split('; ')
				my_watched_episodes = raw_my_watched_episodes.strip()

				for element in alt_title:
					if(len(element) >= 1):
						user.addMalShow(element, my_watched_episodes)

				user.addMalShow(title, my_watched_episodes)

		for show in user.getCustom_Titles():
				user.addMalShow(show, 0)

def getMatch(malShows, serialToSync):
	match = {'Title': "", 'episodesWatched': -1}
	for show in malShows.keys():
		if (fuzz.ratio(show, serialToSync.getSeriesName()) > FUZZ_RATIO):
			match['Title'] = show
			match['episodesWatched'] = malShows[show]['episodesWatched']
	return match

def sync(syncingUser, serialToSync, match):
	print ("Syncing: " + serialToSync.getSeriesName() + ' - ' + str(serialToSync.getSeriesEpisode()) + ' to ' + syncingUser.getUserName())
	if (int(serialToSync.getSeriesEpisode()) > int(match['episodesWatched'])):
		command = "rsync --progress -v -z -e 'ssh -p" + syncingUser.getRemote_Port() + "'" + " \"" + serialToSync.getFilePath() + "\"" + ' ' + "\"" + syncingUser.getRemote_Host() + ":" + syncingUser.getRemote_Download_Dir() + "\""
		process = subprocess.check_call(command, shell=True)
		command = "ssh -p" + syncingUser.getRemote_Port() + ' ' + syncingUser.getRemote_Host() +  " \"mv '" + syncingUser.getRemote_Download_Dir() + '/' + sys.argv[3] + "' '" + syncingUser.getRemote_Download_Dir() + '/' + serialToSync.getFileName() + "'\""
		process = subprocess.check_call(command, shell=True)

		os.chdir(settings['System Settings']['script_location'])
		command = "python3.5 Tools/DiscordAnnounce.py \'" + sys.argv[3] + '\' ' + syncingUser.getUserName()
		process = subprocess.call(command, shell=True)
		hashtoFile(sys.argv[2])

def hashtoFile(theHash):
	os.chdir(settings['System Settings']['script_location'])
	completed = open("Data/completed.txt", "a")
	completed.write(theHash)
	completed.write('\n')
	completed.close()

if __name__=='__main__':
	try:
		settings = readJson()

		#substring the torrent name. If the script throws an exception here later
		#on, switch index to find
		serialToSync = Series()
		serialToSync.setSeriesTitle(sys.argv[3])
		serialToSync.setFilePath(settings['System Settings']['host_download_dir'] + sys.argv[3])

		#for automation tools because PATH is hard
		os.chdir(settings['System Settings']['script_location'])

		if "downloads/Anime" not in sys.argv[1]:
			sys.exit(1)

		jobs = []
		for user in settings['Users']:
			pullMALUserData(settings['Users'].keys())
			syncingUser = User(user, settings['Users'][user])
			getMALShows(syncingUser.getMalDatabaseFileName(), syncingUser)
			match = getMatch(syncingUser.getMalShows(), serialToSync)
			if(match is not None):
				p = multiprocessing.Process(target=sync, args=(syncingUser, serialToSync, match))
				jobs.append(p)
				p.start()

	except Exception as e:
		print (e)
