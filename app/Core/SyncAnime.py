#!/usr/bin/python

import sys
import os
import json
import subprocess
import glob
import xml.etree.ElementTree as ET
import multiprocessing
from fuzzywuzzy import fuzz
from multiprocessing import Process
from collections import OrderedDict

FUZZ_RATIO = 70
validFileExtensions = ['.avi', '.mkv', '.mp4']

class Series:
	seriesName = ""
	episode = -1
	fileName = ""
	filePath = ""
	finalFileName = ""

	def getSeriesName(self):
		return self.seriesName
	def getSeriesEpisode(self):
		return int(self.episode)
	def setSeriesEpisode(self, episodeNumber):
		self.episode = int(episodeNumber)
	def getSeriesFileName(self):
		return self.fileName
	def setSeriesTitle(self, fileName):
		tempName = fileName.replace("_", " ")
		firstHyphen = tempName.rfind(' - ')
		firstCBrac = tempName.index(']', 0)
		seriesName = tempName[firstCBrac+2:firstHyphen]
		episode = tempName[firstHyphen+3:]
		episode = episode[:episode.index(' ',0)]
		filename = seriesName + ' - ' + episode + '.mkv'

		seriesName = seriesName.strip()

		self.fileName = fileName
		self.seriesName = seriesName
		self.episode = episode
		self.finalFileName = filename
	def getFinalName(self):
		return self.finalFileName
	def setFilePath(self, filePath):
		self.filePath = filePath
	def getFullFilePath(self):
		return self.filePath

class User:
	def __init__(self, user, userSettings):
		self.userName = user
		self.remote_port = userSettings['remote_port']
		self.remote_host = userSettings['remote_host']
		self.remote_download_dir = userSettings['remote_download_dir']
		self.discord_ID = userSettings['discord_ID']
		self.custom_titles = userSettings['custom_titles']
		self.AniListShows = {} #titles of AniList shows
		self.AniListDatabaseFileName = "Data/" + user + ".json" #Database File name

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
	def addAniListShow(self, AniListShow, episodesWatched):
		newShow = {AniListShow: {'episodesWatched': int(episodesWatched)}}
		self.AniListShows.update(newShow)
	def getAniListShows(self):
		return self.AniListShows
	def getAniListDatabaseFileName(self):
		return self.AniListDatabaseFileName

def singleFile(torrentTitle):
	if(os.path.isdir(torrentTitle)):
		return False
	else:
		return True

def readJson():
	json_data=open("vars.json").read()
	data = json.loads(json_data, object_pairs_hook=OrderedDict)
	return data #an OrderedDict

def pullAniListUserData(userList):
	for user in userList:
		command = "python3.5 Tools/retAniList.py " + '\"' + user + '\"'
		os.system(command)

def getAniListShows(AniListUserFile, user):
	json_data=open(AniListUserFile).read()
	data = json.loads(json_data)

	for bigList in data:
		if(bigList['status'] == "CURRENT" or bigList['status'] == "PLANNING"):
			for entry in bigList['entries']:
				title = entry['media']['title']['romaji']
				alt_title = entry['media']['synonyms']
				my_watched_episodes = entry['progress']

				for element in alt_title:
					if(len(element) >= 1):
						user.addAniListShow(element, my_watched_episodes)

				if(entry['media']['title']['english'] != None):
					user.addAniListShow(entry['media']['title']['english'], my_watched_episodes)

				user.addAniListShow(title, my_watched_episodes)

	for show in user.getCustom_Titles():
			user.addAniListShow(show, 0)

def getMatches(AniListShows, listOfValidFiles):
	matches = []

	for validFile in listOfValidFiles:
		for show in AniListShows.keys():
			if (fuzz.ratio(show, validFile.getSeriesName()) > FUZZ_RATIO) and validFile not in matches:
				if validFile.getSeriesEpisode() > AniListShows[show]['episodesWatched']:
					matches.append(validFile)
	return matches

def userLoop(settings, isSingleFile, user):
	pullAniListUserData(settings['Users'].keys())
	syncingUser = User(user, settings['Users'][user]) #name, name data
	getAniListShows(syncingUser.getAniListDatabaseFileName(), syncingUser)

	# return either list of one match, or multiple
	listOfValidFiles = []

	if(isSingleFile == True):
		serialToSync = Series()
		serialToSync.setSeriesTitle(sys.argv[3])
		serialToSync.setFilePath(settings['System Settings']['host_download_dir'] + sys.argv[3])
		listOfValidFiles.append(serialToSync)
	else:
		#glob the files here as a list of files
		print ('Globbing')
		os.chdir(settings['System Settings']['host_download_dir'] + sys.argv[3])
		for fileExtension in validFileExtensions:
			fileExtension = "*" + fileExtension #regexify it
			for fileTitle in sorted(glob.glob(fileExtension)):
				serialToSync = Series()
				serialToSync.setSeriesTitle(fileTitle)
				serialToSync.setFilePath(settings['System Settings']['host_download_dir'] + sys.argv[3] + '/' + fileTitle)
				listOfValidFiles.append(serialToSync)

		os.chdir(settings['System Settings']['script_location'])

	matches = getMatches(syncingUser.getAniListShows(), listOfValidFiles)
	if(matches is not None):
		for match in matches:
			#TODO fix multiple matches
			print (match.getSeriesName())
			sync(syncingUser, match)

def sync(syncingUser, serialToSync):
	if(syncingUser.getRemote_Host() != ''):
		print ("Syncing: " + serialToSync.getSeriesName() + ' - ' + str(serialToSync.getSeriesEpisode()) + ' to ' + syncingUser.getUserName())
		if(settings['System Settings']['individual folders'] == "True"):
			command = "ssh -p" + syncingUser.getRemote_Port() + ' ' + syncingUser.getRemote_Host() + " \"mkdir -p " + syncingUser.getRemote_Download_Dir() + '/' +  serialToSync.getSeriesName().replace(" ", "\ ") + '"'
			process = subprocess.check_call(command, shell=True)
			command = "rsync --progress -v -z -e 'ssh -p" + syncingUser.getRemote_Port() + "'" + " \"" + serialToSync.getFullFilePath() + "\"" + ' ' + "\"" + syncingUser.getRemote_Host() + ":" + syncingUser.getRemote_Download_Dir() + '/' + serialToSync.getSeriesName().replace(" ", "\ ") + "\""
			process = subprocess.check_call(command, shell=True)
			command = "ssh -p" + syncingUser.getRemote_Port() + ' ' + syncingUser.getRemote_Host() +  " \"mv '" + syncingUser.getRemote_Download_Dir() + serialToSync.getSeriesName() + '/' + serialToSync.getSeriesFileName() + "' '" + syncingUser.getRemote_Download_Dir() + '/' + serialToSync.getSeriesName() + '/' + serialToSync.getFinalName() + "'\""
			process = subprocess.check_call(command, shell=True)
		elif(settings['System Settings']['individual folders'] == "False"):
			command = "rsync --progress -v -z -e 'ssh -p" + syncingUser.getRemote_Port() + "'" + " \"" + serialToSync.getFullFilePath() + "\"" + ' ' + "\"" + syncingUser.getRemote_Host() + ":" + syncingUser.getRemote_Download_Dir() + "\""
			process = subprocess.check_call(command, shell=True)
			command = "ssh -p" + syncingUser.getRemote_Port() + ' ' + syncingUser.getRemote_Host() +  " \"mv '" + syncingUser.getRemote_Download_Dir() + '/' + serialToSync.getSeriesFileName() + "' '" + syncingUser.getRemote_Download_Dir() + '/' + serialToSync.getFinalName() + "'\""
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

#TODO sys.argv[1] is the same as setFilePath(...) deal with it or refactor it out
if __name__=='__main__':
	try:
		settings = readJson()
		isSingleFile = singleFile(sys.argv[1])
		#for automation tools because PATH is hard
		os.chdir(settings['System Settings']['script_location'])

		#TODO change to check if part of host host_download_dir is in sys.argv[1]
		if "downloads/Anime" not in sys.argv[1]:
			sys.exit(1)

		jobs = []

		for user in settings['Users']:
			p = multiprocessing.Process(target=userLoop, args=(settings, isSingleFile, user))
			jobs.append(p)
			p.start()

	except Exception as e:
		print (e)
