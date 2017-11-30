#!/usr/bin/python

import sys
import os
import retMal
import linecache
import vars
import xml.etree.ElementTree as ET
import multiprocessing
from multiprocessing import Process

#for automation tools because PATH is hard
os.chdir(vars.script_loc)

filePath = vars.host_download_dir + sys.argv[3]
path = sys.argv[1]

if "seedbox/downloads/Anime" not in path:
    sys.exit()

def sync (x, hashed):
    print "Series: " + seriesName
    print "Episode: " + episode
    print x

    index = 0
    found = "false"

    command = "python retMal.py " + '\"' + vars.usernames[x] + '\"'
    os.system(command)
    file_input = open("flags", 'rb')

    exists = file_input.read(1)
    database = vars.usernames[x] + ".xml"

    if exists == '0':
        sys.exit()
    else:
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
                            if title == seriesName or element == seriesName:
                                found = "true"

        if x == 0:
            listLen = custom_title_Avi_len
            customTitleList = vars.custom_title_Avi
        elif x == 1:
            listLen = custom_title_Kan_len
            customTitleList = vars.custom_title_Kan

        while index < listLen and found == "false":
            CustomTitle = customTitleList[index].strip()
            if CustomTitle == seriesName:
                found = "true"
            index+=1;

        if found == "true":
            if episode > int(my_watched_episodes):
                if x == 0:
                    found = "true"
                    command = "rsync --progress -v -z -e 'ssh -p" + vars.userport1 + "'" + " \"" + filePath + "\"" + ' ' + "\"" + vars.a_host + ":" + vars.remote_download_dir1 + "\""
                    os.system(command)
                    command = "ssh -p" + vars.userport1 + ' ' + vars.a_host +  " \"mv '" + vars.remote_download_dir1 +  sys.argv[3] + "' '" + vars.remote_download_dir1 + filename + "'\""
		    os.system(command)
                    command = "echo \'/msg Smoothtalk " + sys.argv[3] + " uploaded and renamed successfully\' > " + vars.irrsi_rc_loc
		    os.system(command)
                    command = "echo \'/msg John_Titor " + sys.argv[3] + " uploaded and renamed successfully\' > " + vars.irrsi_rc_loc
		    os.system(command)
                elif x == 1:
                    found = "true"
                    command = "rsync --progress -v -z -e 'ssh -p" + vars.userport2 + "'" + " \"" + filePath + "\"" + ' ' + "\"" + vars.k_host + ":" + vars.remote_download_dir2 + "\""
                    os.system(command)
                    command = "ssh -p" + vars.userport2 + ' ' + vars.k_host +  " \"mv '" + vars.remote_download_dir2 +  sys.argv[3] + "' '" + vars.remote_download_dir2 + filename + "'\""
                    os.system(command)
                    command = "echo '/msg localhost " + sys.argv[3] + " uploaded and renamed successfully\' > " + vars.irrsi_rc_loc
                    os.system(command)
            if hashed == 0:
                completed = open("completed.txt", "a")
                completed.write(hash)
                completed.write('\n')
                completed.close()
                hashed = 1
            elif x == 1:
                if hashed == 0:
                    completed = open("completed.txt", "a")
                    completed.write(hash)
                    completed.write('\n')
                    completed.close()

        command = "rm flags"
	os.system(command)
    return

    #     if found == "true":
    #         if episode > int(my_watched_episodes):
    #             tempSeriesName = seriesName.replace(" ", "\ ")
    #             if x == 0:
    #                 if seriesName.find(' ') != -1: #series has space
    #                     found = "true"
    #                     command = "rsync -aq --rsync-path='mkdir -p " + vars.remote_download_dir1 + tempSeriesName + "/ && rsync'" + " --progress -v -z -e 'ssh -p" + vars.userport1 + "'" + " \"" + filePath + "\"" + ' ' + "\"" + vars.a_host + ":" + vars.remote_download_dir1 + tempSeriesName + "/" + "\""
    #                     os.system(command)
    #                     command = "ssh -p" + vars.userport1 + ' ' + vars.a_host +  " \"mv '" + vars.remote_download_dir1 + seriesName + '/' + sys.argv[3] + "' '" + vars.remote_download_dir1 + tempSeriesName + '/' + filename + "'\""
    #                     os.system(command)
    #                 else:
    #                     found = "true"
    #                     command = "rsync -aq --rsync-path='mkdir -p " + vars.remote_download_dir1 + seriesName + "/ && rsync'" + " --progress -v -z -e 'ssh -p" + vars.userport1 + "'" + " \"" + filePath + "\"" + ' ' + "\"" + vars.a_host + ":" + vars.remote_download_dir1 + tempSeriesName + "/" + "\""
    #                     os.system(command)
    #                     command = "ssh -p" + vars.userport1 + ' ' + vars.a_host +  " \"mv '" + vars.remote_download_dir1 + seriesName + '/' + sys.argv[3] + "' '" + vars.remote_download_dir1 + seriesName + '/' + filename + "'\""
    #                     os.system(command)
    #                 command = "echo \'/msg Smoothtalk " + sys.argv[3] + " uploaded and renamed successfully\' > " + vars.irrsi_rc_loc
    #                 os.system(command)
    #                 command = "echo \'/msg John_Titor " + sys.argv[3] + " uploaded and renamed successfully\' > " + vars.irrsi_rc_loc
    #                 os.system(command)
    #             elif x == 1:
    #                 if seriesName.find(' ') != -1: #series has space
    #                     found = "true"
    #                     command = "rsync -aq --rsync-path='mkdir -p " + vars.remote_download_dir2 + tempSeriesName + "/ && rsync'" + " --progress -v -z -e 'ssh -p" + vars.userport2 + "'" + " \"" + filePath + "\"" + ' ' + "\"" + vars.k_host + ":" + vars.remote_download_dir22 + tempSeriesName + "/" + "\""
    #                     os.system(command)
    #                     command = "ssh -p" + vars.userport2 + ' ' + vars.k_host +  " \"mv '" + vars.remote_download_dir2 + seriesName + '/' + sys.argv[3] + "' '" + vars.remote_download_dir2 + tempSeriesName + '/' + filename + "'\""
    #                     os.system(command)
    #                 else:
    #                     found = "true"
    #                     command = "rsync -aq --rsync-path='mkdir -p " + vars.remote_download_dir2 + seriesName + "/ && rsync'" + " --progress -v -z -e 'ssh -p" + vars.userport2 + "'" + " \"" + filePath + "\"" + ' ' + "\"" + vars.k_host + ":" + vars.remote_download_dir2 + tempSeriesName + "/" + "\""
    #                     os.system(command)
    #                     command = "ssh -p" + vars.userport2 + ' ' + vars.k_host +  " \"mv '" + vars.remote_download_dir2 + seriesName + '/' + sys.argv[3] + "' '" + vars.remote_download_dir2 + seriesName + '/' + filename + "'\""
    #                     os.system(command)
    #                 command = "echo '/msg localhost " + sys.argv[3] + " uploaded and renamed successfully\' > " + vars.irrsi_rc_loc
    #                 os.system(command)
    #         if hashed == 0:
    #             completed = open("completed.txt", "a")
    #             completed.write(hash)
    #             completed.write('\n')
    #             completed.close()
    #             hashed = 1
    #         elif x == 1:
    #             if hashed == 0:
    #                 completed = open("completed.txt", "a")
    #                 completed.write(hash)
    #                 completed.write('\n')
    #                 completed.close()
    #
    #     command = "rm flags"
	# os.system(command)
    # return

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
user_len = len(vars.usernames)
custom_title_Avi_len = len(vars.custom_title_Avi)
custom_title_Kan_len = len(vars.custom_title_Kan)

if __name__=='__main__':
    jobs = []
    for x in range(len(vars.usernames)):
        p = multiprocessing.Process(target=sync, args=(x,hashed,))
        jobs.append(p)
        p.start()
