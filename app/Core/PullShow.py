#!/usr/bin/python

import sys
import os
import linecache
import re
import codecs
import glob
import json
import xml.etree.ElementTree as ET
import multiprocessing
import urllib.error
import urllib.request
import simplejson as json
from fuzzywuzzy import fuzz
from trakt.users import User
from multiprocessing import Process
from bs4 import BeautifulSoup
from collections import OrderedDict

class TvShow():
	def __init__(self):
		self.title = ""
		self.last_watched_date = -1
		self.last_watched_episode = -1

	def setTitle(self, title):
		self.title = title
	def getTitle(self):
		return self.title
	def setLast_watched_date(self, Last_watched_date):
		self.last_watched_date = Last_watched_date
	def getLast_watched_date(self):
		return self.last_watched_date
	def setlast_watched_episode(self, Last_watched_episode):
		self.last_watched_episode = Last_watched_episode
	def getlast_watched_episode(self):
		return self.last_watched_episode

def readJson():
	json_data=open("../vars.json").read()
	data = json.loads(json_data, object_pairs_hook=OrderedDict)
	return data #an OrderedDict

def getToken():
	getTokenURL = "https://torrentapi.org/pubapi_v2.php?get_token=get_token"

	try:
		hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3004.3 Safari/537.36'}
		req = urllib.request.Request(getTokenURL, headers=hdr)
		response = urllib.request.urlopen(req)

		soup = BeautifulSoup(response.read(), "html.parser")
		soup2 = soup.prettify()

		token = soup2[10:-3]

		return token
	except urllib.error.HTTPError as e:
		print (e)

def searchTVTorrents(token, database):
	#category 41 is hdtv episodes
	listTorrentsURL = "https://torrentapi.org/pubapi_v2.php?mode=list&category=41&format=json&token="
	requestURL = listTorrentsURL + token

	try:
		hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3004.3 Safari/537.36'}
		req = urllib.request.Request(requestURL, headers=hdr)
		response = urllib.request.urlopen(req)

		soup = BeautifulSoup(response.read(), "html.parser")
		soup2 = soup.prettify()

		output = codecs.open(database, 'wb', 'utf-8')
		output.write(soup2)
		output.close()

	except urllib.error.HTTPError as e:
		print (e)

def fixMagnet(magnet):
	magnet = magnet.strip()
	magnet = magnet.replace("&amp", "")
	magnet = magnet.replace(";tr", "&tr")
	magnet = magnet.replace("dn", "&dn")
	magnet = magnet.replace(";", "")
	return magnet

def getShowDict(torrent_title):
	try:
		data = {'Title': "", 'Season': "", 'Episode': ""}
		regex = r"^.*.S\d\d"
		preTitle = re.findall(regex, torrent_title, re.IGNORECASE)
		preTitle = str(preTitle)
		preTitle = preTitle[2:-6]
		title = preTitle.replace('.',' ')
		data['Title'] = title

		regex = r"S\d\dE\d\d"
		tempSandE = str(re.findall(regex, torrent_title, re.IGNORECASE))

		regex = r"\d\d"
		seasonAndEpisodeNumbers = re.findall(regex, tempSandE)

		season = seasonAndEpisodeNumbers[:1]
		episode = seasonAndEpisodeNumbers[1:]
		data['Season'] = season[0]
		data['Episode'] = episode[0]

		return data
	except Exception as e:
		#print (str(torrent_title) + " fucked it all up")
		data['Title'] = ""
		data['Season'] = -1
		data['Episode'] = -1
		return data

def getTraktShows():
	allShows = []
	my = User(settings['Users']['Smoothtalk']['traktUserName'])

	for y in range(len(my.watched_shows)):
		theDict = my.watched_shows[y].seasons[-1]

		# gets the episodes (change to -1 to get current season value
		# -2 gets all teh episodes you've watched
		#TODO FIX THIS SHIT
		values = theDict['episodes']
		print (values)
		last_episode_watched = values[-1]

		episode_Number =  last_episode_watched['number']
		date_Watched_At = last_episode_watched['last_watched_at']

		traktShow = TvShow();
		traktShow.setTitle(my.watched_shows[y])
		traktShow.setLast_watched_date(date_Watched_At)
		traktShow.setlast_watched_episode(episode_Number)
		allShows.append(traktShow)

	return allShows

def compare(allShows, settings, matches):
	fileNameKey = "filename"
	magnetKey = "download"

	with open(database, 'r') as f:
		data = json.load(f)
		json_data = json.dumps(data)
		torrents = data.values()

	for i in allShows:
		for sets in torrents:
			for indValues in sets:
				torrent_title = indValues.get(fileNameKey)
				magnet = fixMagnet(indValues.get(magnetKey))

				if("720p" in torrent_title): # contains 720p
					showDict = getShowDict(torrent_title)

					# try:
						# print title.strip() + " - " + 'S' + season[0] + 'E' + episode[0] + ".mkv"
					# except:
						# print "unable to title, shitty scene groups"
					if(fuzz.ratio(str(i.getTitle())[9:].lower(), showDict['Title'].lower()) > 70 and showDict['Episode'] > i.getlast_watched_episode):
						regex = r"id=.*.="

						dledShowsFile = open('dledshows', 'a+')
						alreadyDLShows = dledShowsFile.read().split("\n")

						epititle = showDict['Title'] + '-S' + showDict['Season'] + 'E' + showDict['Episode']

						if epititle not in alreadyDLShows:
							print ("Downloading")
							fileWithQuotes = '"' + showDict['Title'].strip() + " - " + 'S' + showDict['Season'] + 'E' + showDict['Episode'] + ".torrent" + '"'

							matchDict = {'File': fileWithQuotes}
							magnetDict = {'Magnet': magnet}
							matchDict.update(magnetDict)

							matches.append(matchDict)

							dledShowsFile.write(epititle+'\n')

						dledShowsFile.close()

def generateMagnets(matches):
	for show in matches:
		# command = "python Magnet_To_Torrent2.py -m " + '"' + show['Magnet'] + '"' + " -o " + show['File']
		# os.system(command)
        #
		# command = "mv " + show['File'] + ' ' + settings['System Settings']['watch_dir']
		command = "echo \"it worked\""
		os.system(command)

settings = readJson()
os.chdir(settings['System Settings']['script_location'])

database = "RarBG" + ".json"
matches = []

token = getToken()
searchTVTorrents(token, database)
allShows = getTraktShows()
compare(allShows, settings, matches)
generateMagnets(matches)
