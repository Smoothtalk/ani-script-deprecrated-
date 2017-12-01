#!/usr/bin/python

import feedparser
import sys
import os
import json
import datetime
import urllib
import xml.etree.ElementTree as ET
from collections import OrderedDict

reload(sys)
sys.setdefaultencoding('utf-8')

def readJson():
	json_data=open("vars.json").read()
	data = json.loads(json_data, object_pairs_hook=OrderedDict)
	return data #an OrderedDict

settings = readJson()

#anime object to store relevant deets
class anime():
	show_id = -1
	title = ""
	alt_titles = []
	last_dl = -1
	status = -1
	last_watched = -1
	def __eq__(self, other):
		return self.show_id == other.show_id
	def __hash__(self):
		return hash(self.show_id)

userList = settings['Users'].keys()
#pull updated user list from Mal. not /really/ required, but w/e
command = "python retMal.py " + '\"' + userList[0] + '\"'
os.system(command)
command = "python retMal.py " + '\"' + userList[1] + '\"'
os.system(command)

customTitleListA = settings['Users']['Smoothtalk']['custom_titles']
customTitleListK = settings['Users']['shinigamibob']['custom_titles']

currDate = datetime.datetime.today()
lastWeek = currDate - datetime.timedelta(days=7)

allShows = [] #holds all watching and plan to watch shows
for x in range(0,(len(userList))):
	database = userList[x] + ".xml"
	with open(database, 'rt') as f:
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
				if (lastWeek <= seriesEnd <= currDate): #TODO FIX THIS #series_end is within a week of today's date
					allShows.append(tempAnime)

print len(allShows)
allShows = list(set(allShows)) #should have a list of unique shows from both users

#adds the special titles from vars.py, clears tempanime and index before loops
#because technology is weird
index = 0
tempAnime = anime();

#since below these loops you are checking whether the first two words are matching
#check if against the custom_title in vars.py and if the first two words of a title match
#it is considered a dupe
while index < len(customTitleListA):
	tempAnime = anime()
	dupe = "false"
	tempAnime.title = customTitleListA[index].strip()
	for i in allShows:
		if i.title.split()[:2] == tempAnime.title.split()[:2]:
			dupe = "true"
	if dupe == "false":
		allShows.append(tempAnime)
	index+=1;

index = 0
tempAnime = anime();
while index < len(customTitleListK):
	tempAnime = anime()
	dupe = "false"
	tempAnime.title = customTitleListK[index].strip()
	for i in allShows:
		if i.title.split()[:2] == tempAnime.title.split()[:2]:
			dupe = "true"
	if dupe == "false":
		allShows.append(tempAnime)
	index+=1;

truncShows = []
for i in allShows:
  truncShows.append(' '.join(i.title.split()[:2])) #gets the first two words in the title for easier processing

#for i in truncShows:
#s	print i.encode('utf-8').strip()

print len(allShows)
hsFeed = feedparser.parse('http://horriblesubs.info/rss.php?res=720')
hsReleases = hsFeed.get('entries') #list of all releases

#for i in hsReleases:
#	title = i['title']
#	magnetLink = i['links'][0]['href']
#	guid = str(magnetLink[20:52])

matches = []
for i in hsReleases:
	for j in truncShows:
		if j in i.title: #match user shows to hs torrent title. update required to match against alt titles as well #TODO add fuzzy check
			if len(j) != 1: #DARN 'K' ANIME MESSING EVERYTHING UP, since the title splitter on line 130 picks up only 'k' as the title
				matches.append(i) #it matches any anime title with 'k' in it

tidfile = open('tidfile', 'a+') #stores torrent tids so that they wont download again
existingTIDs = tidfile.read().split("\n")

for i in matches:
	print i.title
	title = i.title
	url = i.link
	tid = str(url[20:52]) #get tid from torrent url

	if tid not in existingTIDs: #if tid doesn't already exist, download
		fileWithQuotes = '"' + title + ".torrent" + '"'
		command = "python Magnet_To_Torrent2.py -m " + '"' + url + '"' + " -o " + fileWithQuotes
		os.system(command)

		command = "mv " + fileWithQuotes + ' ' + settings['System Settings']['watch_dir']
		os.system(command)
		tidfile.write(tid+"\n")

tidfile.close()
print len(matches)
