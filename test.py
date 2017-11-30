#!/usr/bin/python

import sys
import os
import retMal
import linecache
import vars
import re
import codecs
import glob
import json
import xml.etree.ElementTree as ET
import multiprocessing
import urllib2
import simplejson as json
from pprint import pprint
from urllib2 import Request, urlopen
from trakt.users import User
from multiprocessing import Process
from bs4 import BeautifulSoup

class TvShow():
	title = ""
	last_watched_date = -1
	last_watched_episode = -1
	
os.chdir(vars.script_loc)
database = "RarBG" + ".json"
allShows = []

def getToken():
	getTokenURL = "https://torrentapi.org/pubapi_v2.php?get_token=get_token"
	
	try:
		req = urllib2.Request(getTokenURL, None)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3004.3 Safari/537.36')
		response = urllib2.urlopen(req)

		soup = BeautifulSoup(response.read(), "html.parser")
		soup2 = soup.prettify()
		
		token = soup2[10:-3]

		return token
	except urllib2.HTTPError,err:
		print err
		
		
def searchTVTorrents(token):
	#category 41 is hdtv episodes
	listTorrentsURL = "https://torrentapi.org/pubapi_v2.php?mode=list&category=41&format=json&token="
	requestURL = listTorrentsURL + token
	
	try:
		req = urllib2.Request(requestURL, None)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3004.3 Safari/537.36')
		response = urllib2.urlopen(req)
		
		soup = BeautifulSoup(response.read(), "html.parser")
		soup2 = soup.prettify()
		
		output = codecs.open(database, 'wb', 'utf-8')
		output.write(soup2)
		output.close()
		
	except urllib2.HTTPError,err:
		print err
		
		
def compare():
	fileNameKey = "filename"
	magnetKey = "download"
	
	#for loop for users
	for x in range(len(vars.trUserNames)):
		my = User(vars.trUserNames[x])
		
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
			allShows.append(traktShow)
		
		# traktShow = TvShow();
		# traktShow.title = "<TVShow> "
		# traktShow.last_watched_episode = 
		# allShows.append(traktShow)
		
		traktShow = TvShow();
		traktShow.title = "<TVShow> NCIS Los Angeles"
		traktShow.last_watched_episode = 11
		allShows.append(traktShow)
	
	with open(database, 'r') as f:
		data = json.load(f)
		json_data = json.dumps(data)
		torrents = data.values()
		
	for i in allShows:
		for sets in torrents:
			for indValues in sets:
				torrent_title = indValues.get(fileNameKey)
				
				magnet = indValues.get(magnetKey)
				magnet = magnet.strip()
				magnet = magnet.replace("&amp", "")
				magnet = magnet.replace(";tr", "&tr")
				magnet = magnet.replace("dn", "&dn")
				magnet = magnet.replace(";", "")
				
				if("720p" in torrent_title): # contains 720p
							regex = r"^.*.S\d\d"
							preTitle = re.findall(regex, torrent_title, re.IGNORECASE)
							preTitle = str(preTitle)
							preTitle = preTitle[2:-6]
							title = preTitle.replace('.',' ')
									
							regex = r"S\d\dE\d\d"
							tempSandE = str(re.findall(regex, torrent_title, re.IGNORECASE))
							
							regex = r"\d\d"
							seasonAndEpisodeNumbers = re.findall(regex, tempSandE)
							
							season = seasonAndEpisodeNumbers[:1]
							episode = seasonAndEpisodeNumbers[1:]
							
							# try:
								# print title.strip() + " - " + 'S' + season[0] + 'E' + episode[0] + ".mkv"
							# except:
								# print "unable to title, shitty scene groups"
								
							if(str(i.title)[9:].lower() == title.lower() and episode > i.last_watched_episode):
								print "Matched"
								regex = r"id=.*.="

								dledShowsFile = open('dledshows', 'a+')
								alreadyDLShows = dledShowsFile.read().split("\n")
								
								epititle = episode[0]+title
								if epititle not in alreadyDLShows:
									fileWithQuotes = '"' + title.strip() + " - " + 'S' + season[0] + 'E' + episode[0] + ".torrent" + '"'
									command = "python Magnet_To_Torrent2.py -m " + '"' + magnet + '"' + " -o " + fileWithQuotes
									os.system(command)
									
									command = "mv " + fileWithQuotes + ' ' + "../downloads/watch/"
									os.system(command)
									
									dledShowsFile.write(epititle+'\n')
									
								dledShowsFile.close()
			
token = getToken()
searchTVTorrents(token)
compare()