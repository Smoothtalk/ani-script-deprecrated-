#!/usr/bin/python

import sys
import os
import retMal
import linecache
import json
import time
import subprocess
import xml.etree.ElementTree as ET
import multiprocessing
from fuzzywuzzy import fuzz
from multiprocessing import Process
from collections import OrderedDict

def readJson():
	json_data=open("vars.json").read()
	data = json.loads(json_data, object_pairs_hook=OrderedDict)
	return data #an OrderedDict

def sync (x, hashed, settings, seriesName, episode, filename, userList, custom_title_Avi_len, custom_title_Kan_len):
	print "Series: " + seriesName
	print "Episode: " + episode
	print x

	index = 0
	found = "false"

	command = "python retMal.py " + '\"' + userList[x] + '\"'
	os.system(command)
	file_input = open("flags", 'rb')

	database = userList[x] + ".xml"

	with open(database, 'rt') as f:
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
					if found == "false":
						# if title == seriesName or element == seriesName:
						if (fuzz.ratio(title, seriesName) > 70 or fuzz.ratio(element, seriesName) > 70):
							found = "true"

        if x == 0:
            listLen = custom_title_Avi_len
            customTitleList = settings['Users']['Smoothtalk']["custom_titles"]
        elif x == 1:
            listLen = custom_title_Kan_len
            customTitleList = settings['Users']['shinigamibob']["custom_titles"]

        while index < listLen and found == "false":
            CustomTitle = customTitleList[index].strip()
            if CustomTitle == seriesName:
                found = "true"
            index+=1;

        if found == "true" or (x == 0 and seriesName == 'Ame-con!!'):
            if episode > int(my_watched_episodes):
				if x == 0:
					found = "true"
					command = "rsync --progress -v -z -e 'ssh -p" + settings['Users']['Smoothtalk']['remote_port'] + "'" + " \"" + filePath + "\"" + ' ' + "\"" + settings['Users']['Smoothtalk']['remote_host'] + ":" + settings['Users']['Smoothtalk']['remote_download_dir'] + "\""
					process = subprocess.check_call(command, shell=True)
					command = "ssh -p" + settings['Users']['Smoothtalk']['remote_port'] + ' ' + settings['Users']['Smoothtalk']['remote_host'] +  " \"mv '" + settings['Users']['Smoothtalk']['remote_download_dir'] +  sys.argv[3] + "' '" + settings['Users']['Smoothtalk']['remote_download_dir'] + filename + "'\""
					process = subprocess.check_call(command, shell=True)
					command = "python3.5 discordAnnounce.py \'" + sys.argv[3] + '\' ' + "0"
					process = subprocess.call(command, shell=True)
					if hashed == 0:
						os.chdir(settings['System Settings']['script_location'])
						completed = open("completed.txt", "a")
						completed.write(hash)
						completed.write('\n')
						completed.close()
						hashed = 1
				elif x == 1:
					found = "true"
					print "Kan"
					command = "rsync --progress -v -z -e 'ssh -p" + settings['Users']['shinigamibob']['remote_port'] + "'" + " \"" + filePath + "\"" + ' ' + "\"" + settings['Users']['shinigamibob']['remote_host'] + ":" + settings['Users']['shinigamibob']['remote_download_dir'] + "\""
					process =  subprocess.check_call(command, shell=True)
					command = "ssh -p" + settings['Users']['shinigamibob']['remote_port'] + ' ' + settings['Users']['shinigamibob']['remote_host'] +  " \"mv '" + settings['Users']['shinigamibob']['remote_download_dir'] + sys.argv[3] + "' '" + settings['Users']['shinigamibob']['remote_download_dir'] + filename + "'\""
					process = subprocess.check_call(command, shell=True)
					command = "python3.5 discordAnnounce.py \'" + sys.argv[3] + '\' ' + "1"
					process = subprocess.call(command, shell=True)
					if hashed == 0:
						os.chdir(settings['System Settings']['script_location'])
						completed = open("completed.txt", "a")
						completed.write(hash)
						completed.write('\n')
						completed.close()
						hashed = 1

	return

if __name__=='__main__':
    settings = readJson()
    #change sys.argv[1] to renamed
    hash = sys.argv[2]
    hashed = 0

    #substring the torrent name. If the script throws an exception here later
    #on, switch index to find
    tempName = sys.argv[3].replace("_", " ")
    firstHyphen = tempName.rfind(' - ')
    firstCBrac = tempName.index(']', 0)
    seriesName = tempName[firstCBrac+2:firstHyphen]
    episode = tempName[firstHyphen+3:]
    episode = episode[:episode.index(' ',0)]
    filename = seriesName + ' - ' + episode + '.mkv'

    seriesName = seriesName.strip()
    custom_title_Avi_len = len(settings['Users']['Smoothtalk']['custom_titles'])
    custom_title_Kan_len = len(settings['Users']['shinigamibob']['custom_titles'])

    #for automation tools because PATH is hard
    os.chdir(settings['System Settings']['script_location'])
    filePath = settings['System Settings']['host_download_dir'] + sys.argv[3]
    path = sys.argv[1]

    userList = settings['Users'].keys()

    if "downloads/Anime" not in path:
        sys.exit(1)

    jobs = []
    for x in range(len(settings['Users'])):
        p = multiprocessing.Process(target=sync, args=(x, hashed, settings, seriesName, episode, filename, userList, custom_title_Avi_len, custom_title_Kan_len))
        jobs.append(p)
        p.start()
