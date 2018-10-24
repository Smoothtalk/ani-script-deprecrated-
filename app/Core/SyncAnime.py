#!/usr/bin/python

import sys
import os
import json
import subprocess
import glob
import xml.etree.ElementTree as ET
import multiprocessing
import transmissionrpc
from fuzzywuzzy import fuzz
from multiprocessing import Process
from collections import OrderedDict

FUZZ_RATIO = 70
TRANSMISSION_PORT = 9091
validFileExtensions = ['.avi', '.mkv', '.mp4']

class Series:
	seriesName = ""
	episode = -1
	filePath = ""
	fileNameRaw = ""
	fileNameClean = ""
	torrentHash = sys.argv[2]

	def setSeriesName(self, seriesName):
		self.seriesName = seriesName
	def setSeriesEpisode(self, episodeNumber):
		self.episode = int(episodeNumber)
	def setFileNameRaw(self, fileName):
		self.fileNameRaw = fileName
	def setFileNameClean(self, fileName):
		self.fileNameClean = fileName
	def setFilePath(self, filePath):
		self.filePath = filePath

	def getSeriesName(self):
		seriesName = self.encodeForFileSystem(self.seriesName)
		return seriesName
	def getSeriesEpisode(self):
		return int(self.episode)
	def getFileNameRaw(self):
		fileNameRaw = self.encodeForFileSystem(self.fileNameRaw)
		return fileNameRaw
	def getFileNameClean(self):
		fileNameClean = self.encodeForFileSystem(self.fileNameClean)
		return fileNameClean
	def getFilePath(self):
		filePath = self.encodeForFileSystem(self.filePath)
		return filePath

	def encodeForFileSystem(self, obj):
		if(type(obj) == str):
			try:
				if("'" in obj):
					obj = obj.replace("'", "\'\\'\'")
				return obj
			except:
				print ('oops')

	def setSeriesTitle(self, fileName):
		#TODO fix j'darc
		tempName = fileName.replace("_", " ")

		firstHyphen = tempName.rfind(' - ')
		firstCBrac = tempName.index(']', 0)
		seriesName = tempName[firstCBrac+2:firstHyphen]
		episode = tempName[firstHyphen+3:]
		episode = episode[:episode.index(' ',0)]
		filename = seriesName + ' - ' + episode + '.mkv'

		self.setSeriesEpisode(episode)
		self.setFileNameRaw(fileName)
		self.setFileNameClean(filename)
		self.setSeriesName(seriesName)

	def getTorrentHash(self):
		return self.torrentHash

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
		command = "python3 Tools/retAniList.py " + '\"' + user + '\"'
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

def userLoop(settings, isSingleFileDownload, user, returnDict):
	pullAniListUserData(settings['Users'].keys())
	syncingUser = User(user, settings['Users'][user]) #name, name data
	getAniListShows(syncingUser.getAniListDatabaseFileName(), syncingUser)

	# return either list of one match, or multiple
	listOfValidFiles = []

	if(isSingleFileDownload == True):
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
			print ("Matched: " + match.getSeriesName())
			status = sync(syncingUser, match)
			returnDict[user] = status

def sync(syncingUser, serialToSync):
	if(syncingUser.getRemote_Host() != ''):
		print ("Syncing: " + serialToSync.getSeriesName() + ' - ' + str(serialToSync.getSeriesEpisode()) + ' to ' + syncingUser.getUserName())
		#TODO wrap in try except
		if(settings['System Settings']['individual folders'] == "True"):
			#.replace(" ", "\ ") after get seriesName
			command = "mkdir -p \'" + syncingUser.getRemote_Download_Dir() + serialToSync.getSeriesName() + '\''
			process = subprocess.check_call(command, shell=True)
			command = "cp \'" + serialToSync.getFilePath() + "\' \'" + syncingUser.getRemote_Download_Dir() + serialToSync.getSeriesName() + '\''
			process = subprocess.check_call(command, shell=True)
			command = "mv '" + syncingUser.getRemote_Download_Dir() + serialToSync.getSeriesName() + '/' + serialToSync.getFileNameRaw() + "' '" + syncingUser.getRemote_Download_Dir() + serialToSync.getSeriesName() + '/' + serialToSync.getFileNameClean() + '\''
			process = subprocess.check_call(command, shell=True)
			command = "chown 1000:1000 \'" + syncingUser.getRemote_Download_Dir() + serialToSync.getSeriesName() + '/' + serialToSync.getFileNameClean()  + '\''
			process = subprocess.check_call(command, shell=True)
			command = "chmod 0770 \'" + syncingUser.getRemote_Download_Dir() + serialToSync.getSeriesName() + '/' + serialToSync.getFileNameClean()  + '\''
			process = subprocess.check_call(command, shell=True)
		elif(settings['System Settings']['individual folders'] == "False"):
			command = "cp \'" + serialToSync.getFilePath() + "\' \'" + syncingUser.getRemote_Download_Dir() + '\''
			process = subprocess.check_call(command, shell=True)
			command = "mv '" + syncingUser.getRemote_Download_Dir() + '/' + serialToSync.getFileNameRaw() + "' '" + syncingUser.getRemote_Download_Dir() + '/' + serialToSync.getFileNameClean() + '\''
			process = subprocess.check_call(command, shell=True)
			command = "chown 1000:1000 \'" + syncingUser.getRemote_Download_Dir() + '/' + serialToSync.getFileNameClean() + '\''
			process = subprocess.check_call(command, shell=True)
			command = "chmod 0770 \'" + syncingUser.getRemote_Download_Dir() + '/' + serialToSync.getFileNameClean() + '\''
			process = subprocess.check_call(command, shell=True)
		os.chdir(settings['System Settings']['script_location'])
		command = "python3 Tools/DiscordAnnounce.py \'" + serialToSync.getFileNameClean() + '\' ' + syncingUser.getUserName()
		# print (command)
		process = subprocess.call(command, shell=True)
		hashtoFile(serialToSync.getTorrentHash())
		return True

def hashtoFile(theHash):
	os.chdir(settings['System Settings']['script_location'])
	completed = open("Data/completed.txt", "a")
	completed.write(theHash)
	completed.write('\n')
	completed.close()

#TODO sys.argv[1] is the same as setFilePath(...) deal with it or refactor it out
if __name__=='__main__':
	try:
		# print ('arg1: ' + sys.argv[1])
		# print ('arg2: ' + sys.argv[2])
		# print ('arg3: ' + sys.argv[3])
		settings = readJson()
		#check for list index out of range
		isSingleFileDownload = singleFile(sys.argv[1])
		#for automation tools because PATH is hard
		os.chdir(settings['System Settings']['script_location'])

		#TODO change to check if part of host host_download_dir is in sys.argv[1]
		if "Downloads/Complete" not in sys.argv[1]:
			sys.exit(1)

		jobs = []
		manager = multiprocessing.Manager()
		returnDict = manager.dict()

		for user in settings['Users']:
			p = multiprocessing.Process(target=userLoop, args=(settings, isSingleFileDownload, user, returnDict))
			jobs.append(p)
			p.start()

		for process in jobs:
			process.join()

		#TODO
		#construct failure dictionary by mapping if sync == false to each key
		#each key has a dictionary of values with hte only value being successfully
		#{user1: {sync: true}, user2: {sync: false}, user3: {sync: true}, user4: {sync: false}}
		#-> {user2: false, user4: false}
		#if fail dict.length > 1
		# print failed to sync to: user2, user4

		#temp
		if(False in returnDict.values()):
			print ('Failed to sync to someone')
		else:
			tc = transmissionrpc.Client('localhost', port=TRANSMISSION_PORT)
			# tc.remove_torrent(sys.argv[2], True)

	except Exception as e:
		print (e)
