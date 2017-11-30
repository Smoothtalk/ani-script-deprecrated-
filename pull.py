import re
import codecs
import xml.etree.ElementTree as ET
import urllib2
import json
from urllib2 import Request, urlopen
from fuzzywuzzy import fuzz
from trakt.users import User
from bs4 import BeautifulSoup
from collections import OrderedDict

#5 0 * * 0 find /home/seedbox/ani-script/dledshows -size 0 -delete in crontab
#Do we even know who is this TvShow is? -ridiculous hand motions-
class TvShow():
	title = ""
	last_watched_date = -1
	last_watched_episode = -1

HD_TV_Shows_RSS = "https://rarbg.to/rssdd.php?category=41"
database = "RarBG" + ".xml"
allShows = []

def readJson():
	json_data=open("vars.json").read()
	data = json.loads(json_data, object_pairs_hook=OrderedDict)
	return data #an OrderedDict

settings = readJson()

my = User(settings['Users']['Smoothtalk']['trUserName'])

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

try:
	req = urllib2.Request(HD_TV_Shows_RSS)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3004.3 Safari/537.36')
	response = urllib2.urlopen(req)

	soup = BeautifulSoup(response.read(), "html.parser")
	soup2 = soup.prettify()
	output = codecs.open(database, 'wb', 'utf-8')
	output.write(soup2)
	output.close()

	for i in allShows:
		with open(database, 'rt') as f:
			tree = ET.parse(f)
			for node in tree.findall('.//item'):
				raw_torrent_title = node.find('title').text
				raw_link = node.find('link').tail
				raw_pubDate = node.find('pubdate').text

				torrent_title = raw_torrent_title.strip()
				link = raw_link.strip()

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

					print "i.title:", str(i.title)[9:]
					print "title:", title.strip()

					#if(str(i.title)[9:].lower() == title.lower() and episode > i.last_watched_episode):
					if(fuzz.ratio(str(i.title)[9:].lower(), title.lower()) > 70 and episode > i.last_watched_episode):
						print "Matched"

						regex = r"id=.*.="
						preTid = re.findall(regex, link)
						preTid = str(preTid)
						tid = preTid[5:-3]

						dledShowsFile = open('dledshows', 'a+')
						alreadyDLShows = dledShowsFile.read().split("\n")

						epititle = episode[0]+title
						if epititle not in alreadyDLShows:
							req = urllib2.Request(link, None)
							req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3004.3 Safari/537.36')
							response = urllib2.urlopen(req)

							print settings['System Settings']['watch_dir']

							torrentFile = open(settings['System Settings']['watch_dir']+tid+".torrent", "w")
							torrentFile.write(response.read())
							torrentFile.close()
							dledShowsFile.write(episode[0]+title+'\n')

						dledShowsFile.close()

except urllib2.HTTPError,err:
	print err
