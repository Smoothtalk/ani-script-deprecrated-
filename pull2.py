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
	userName = None
	Custom_Titles = []
	dataBaseFileName = None

class anime():
	show_id = None
	title = None
	alt_titles = []
	status = None
	last_watched = None
	def __eq__(self, other):
		return self.show_id == other.show_id
	def __hash__(self):
		return hash(self.show_id)

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
		newUser = userClass()
		newUser.userName = user
		newUser.Custom_Titles = users[user]['custom_titles']
		newUser.dataBaseFileName = user + ".xml"
		userList.append(newUser)

	return userList

def getAllUniqueMALShows(users):
	allShows = [] #holds all watching and plan to watch shows
	currDate = datetime.datetime.today()
	lastWeek = currDate - datetime.timedelta(days=7)

	for user in users:
		with open(user.dataBaseFileName, 'rt') as f:
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
				tempAnime.show_id = show_id
				tempAnime.title = title
				tempAnime.alt_titles = alt_title
				tempAnime.last_watched = my_watched_episodes
				tempAnime.status = series_status
				if series_status == "1" or series_status == "3": #anime series status: 1 is airing, 2 has finished airing 3 is unaired
					allShows.append(tempAnime)
				elif series_status == "2":
					if (lastWeek <= currDate <= seriesEnd): #TODO FIX THIS #series_end is within a week of today's date
						allShows.append(tempAnime)

		#add custom titles here
		for altTitle in user.Custom_Titles:
			tempAnime = anime()
			tempAnime.title = altTitle.strip()
			if(checkDupes(tempAnime.title, allShows)):
				allShows.append(tempAnime)

	print "Length of all shows(dupes included): " + str(len(allShows))
	allShows = list(set(allShows)) #Removes dupes from list
	print "Length of all shows(incl custom title, no dupes): " + str(len(allShows))
	return allShows

def getMatches(releases, allShows, matches):
	for release in releases:
		seriesTitle = getSeriesTitle(release.title)
		for malShow in allShows:
			if(fuzz.ratio(malShow.title.decode('utf-8'), seriesTitle) > FUZZ_RATIO):
				if (len(malShow.title) != 1): #DARN 'K' ANIME MESSING EVERYTHING UP, since the title splitter on line 130 picks up only 'k' as the title
					matches.append(release) #it matches any anime title with 'k' in it
			elif(len(malShow.alt_titles) > 0):
				for altTitle in malShow.alt_titles:
					if(fuzz.ratio(altTitle.decode('utf-8'), seriesTitle) > FUZZ_RATIO):
						matches.append(release)
						pass

	return matches

def makeMagnets(matches):
	tidfile = open('tidfile', 'a+') #stores torrent tids so that they wont download again
	existingTIDs = tidfile.read().split("\n")
	currDate = datetime.datetime.strptime(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S") #getting today with out stupid microseconds
	lastWeek = currDate - datetime.timedelta(days=7)

	for matchedShow in matches:
		print matchedShow.title
		title = matchedShow.title
		url = matchedShow.link

		if ".torrent" in url: #Nyaa RSS
			pubDate = matchedShow.published[:-6]
			datetime_publish = datetime.datetime.strptime(pubDate.encode("utf-8"), '%a, %d %b %Y %H:%M:%S')
			if(lastWeek <= datetime_publish <= currDate):
				tid = str(url[25:31])
				fileWithQuotes = '"' + tid + ".torrent" + '"'
				# command = "wget \'" + url + '\''
			else:
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
settingsUsers = settings['Users'].keys()

#pull updated user list from Mal. not /really/ required, but w/e
pullMALUserData(settingsUsers)
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
