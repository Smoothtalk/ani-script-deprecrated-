#!/usr/bin/python

import feedparser
import sys
import os
import json
import datetime
import urllib
import xml.etree.ElementTree as ET
from collections import OrderedDict
from fuzzywuzzy import fuzz

FUZZ_RATIO = 85

#anime object to store relevant deets
class userClass():
	def __init__(self):
		self.userName = None
		self.Custom_Titles = []
		self.dataBaseFileName = None

	def setUserName(self, userName):
		self.userName = userName
	def getUserName(self):
		return self.userName
	def setCustom_Titles(self, customTitles):
		self.Custom_Titles = customTitles
	def getCustom_Titles(self):
		return self.Custom_Titles
	def setDataBaseFileName(self, dataBaseFileName):
		self.dataBaseFileName = dataBaseFileName
	def getDataBaseFileName(self):
		return self.dataBaseFileName

class anime():
	def __init__(self):
		self.show_id = None
		self.title = None
		self.self.alt_titles = []
		self.status = None
		self.last_watched = None

	def __eq__(self, other):
		return self.show_id == other.show_id
	def __hash__(self):
		return hash(self.show_id)
	def setShow_id(self, show_id):
		self.show_id = show_id
	def getShow_id(self):
		return self.show_id
	def setTitle(self, title):
		self.title = title
	def getTitle(self):
		return self.title
	def setAlt_titles(self, altTitles):
		self.alt_titles = altTitles
	def getAlt_titles(self):
		return self.alt_titles
	def setStatus(self, status):
		self.status = status
	def getStatus(self):
		return self.status
	def setLast_watched(self, last_watched):
		self.last_watched = last_watched
	def getLast_watched(self):
		return self.last_watched

def readJson():
	json_data=open("vars.json").read()
	data = json.loads(json_data, object_pairs_hook=OrderedDict)
	return data #an OrderedDict

def getSeriesTitle(fileName):
	tempName = fileName.replace("_", " ")
	firstHyphen = tempName.rfind(' - ')
	firstCBrac = tempName.index(']', 0)
	seriesName = tempName[firstCBrac+2:firstHyphen]
	return seriesName

def pullMALUserData(userList):
	for user in userList:
		command = "python retMal.py " + '\"' + user + '\"'
		os.system(command)

def checkDupes(animeTitle, showList):
	allTitle = []
	for show in showList:
		allTitle.append(show.title)
		for altTitle in show.alt_titles:
			allTitle.append(allTitle)

	if(animeTitle not in allTitle):
		return True
	else:
		return False

def generateUserObjects(users):
	userList = []

	for user in users:
		dataBaseFileName = user + ".xml"
		newUser = userClass()
		newUser.setUserName(user)
		newUser.setCustom_Titles(users[user]['custom_titles'])
		newUser.setDataBaseFileName(dataBaseFileName)
		userList.append(newUser)

	return userList

def getAllUniqueMALShows(users):
	allShows = [] #holds all watching and plan to watch shows
	currDate = datetime.datetime.today()
	lastWeek = currDate - datetime.timedelta(days=7)
	nextWeek = currDate + datetime.timedelta(days=7)

	for user in users:
		with open(user.getDataBaseFileName(), 'rt') as f:
			tree = ET.parse(f)

		for node in tree.findall('.//anime'):
			raw_status = node.find('my_status').text
			status = raw_status.strip()
			#user's series status: 1 == watching, 2 == completed, 6 == plan to watch
			if (status == '1' or status == '6'):
				show_id = node.find('series_animedb_id').text.strip()
				raw_title = node.find('series_title').text
				raw_alt_title = node.find('series_synonyms').text #this is a list
				series_status = node.find('series_status').text.strip()
				series_end_date = node.find('series_end').text.strip()
				raw_my_watched_episodes = node.find('my_watched_episodes').text
				my_watched_episodes = raw_my_watched_episodes.strip()

				title = raw_title.strip()
				alt_title_unsplit = raw_alt_title.strip()
				alt_title = alt_title_unsplit.split('; ')
				if alt_title[0] == "" :#and len(alt_title) > 1:
					alt_title.remove('')

				if ('-00' not in series_end_date):
					seriesEnd = datetime.datetime.strptime(series_end_date, '%Y-%m-%d') #conversion from string to datetime

				tempAnime = anime()
				tempAnime.setShow_id(show_id)
				tempAnime.setTitle(title)
				tempAnime.setAlt_titles(alt_title)
				tempAnime.setLast_watched(my_watched_episodes)
				tempAnime.setStatus(series_status)
				if series_status == "1" or series_status == "3": #anime series status: 1 is airing, 2 has finished airing 3 is unaired
					allShows.append(tempAnime)
				elif series_status == "2":
					if (lastWeek <= seriesEnd <= nextWeek):
						allShows.append(tempAnime)

		#add custom titles here
		for altTitle in user.getCustom_Titles():
			tempAnime = anime()
			tempAnime.setTitle(altTitle.strip())
			if(checkDupes(tempAnime.getTitle(), allShows)):
				allShows.append(tempAnime)

	print "Length of all shows(dupes included): " + str(len(allShows))
	allShows = list(set(allShows)) #Removes dupes from list
	print "Length of all shows(incl custom title, no dupes): " + str(len(allShows))
	return allShows

def getMatches(releases, allShows, matches):
	for release in releases:
		seriesTitle = getSeriesTitle(release.title)
		for show in allShows:
			if(fuzz.ratio(show.getTitle().decode('utf-8'), seriesTitle) > FUZZ_RATIO):
				if (len(show.getTitle()) != 1): #DARN 'K' ANIME MESSING EVERYTHING UP, since the title splitter on line 130 picks up only 'k' as the title
					matches.append(release) #it matches any anime title with 'k' in it
			elif(len(show.getAlt_titles) > 0):
				for altTitle in show.getAlt_titles:
					if(fuzz.ratio(altTitle.decode('utf-8'), seriesTitle) > FUZZ_RATIO):
						matches.append(release)
						pass

	return matches

def makeMagnets(matches):
	tidfile = open('tidfile', 'a+') #stores torrent tids so that they wont download again
	existingTIDs = tidfile.read().split("\n")
	currDate = datetime.datetime.strptime(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S") #getting today with out stupid microseconds
	lastWeek = currDate - datetime.timedelta(days=7)
	nextWeek = currDate + datetime.timedelta(days=7)

	for matchedShow in matches:
		print matchedShow.title
		title = matchedShow.title
		url = matchedShow.link

		pubDate = matchedShow.published[:-6]
		datetime_publish = datetime.datetime.strptime(pubDate.encode("utf-8"), '%a, %d %b %Y %H:%M:%S')

		if(lastWeek <= datetime_publish <= nextWeek):
			if ".torrent" in url: #Nyaa RSS
					tid = str(url[25:31])
					fileWithQuotes = '"' + tid + ".torrent" + '"'
					# command = "wget \'" + url + '\''
					command = ""
			else: #HS RSS
				tid = str(url[20:52])
				fileWithQuotes = '"' + title + ".torrent" + '"'
				# command = "python Magnet_To_Torrent2.py -m " + '"' + url + '"' + " -o " + fileWithQuotes

		if tid not in existingTIDs: #if tid doesn't already exist, download
			# os.system(command)
			command = "mv " + fileWithQuotes + ' ' + settings['System Settings']['watch_dir']
			os.system(command)
			tidfile.write(tid+"\n")
	tidfile.close()

def getFeeds(Rss_Feeds):
	feedList = []

	for feed in Rss_Feeds:
		feedList.append(Rss_Feeds[feed])

	return feedList

reload(sys)
sys.setdefaultencoding('utf-8')

settings = readJson()

#pull updated user list from Mal. not /really/ required, but w/e
pullMALUserData(settings['Users'].keys())
userObjects = generateUserObjects(settings['Users'])
allShows = getAllUniqueMALShows(userObjects)
feedUrls = getFeeds(settings['Rss Feeds'])

matches = []
for url in feedUrls:
	if(url != ""):
		feed = feedparser.parse(url)
		releases = feed.get('entries')
		matches = getMatches(releases, allShows, matches)
		makeMagnets(matches)

print "Length of matches: " + str(len(matches))
