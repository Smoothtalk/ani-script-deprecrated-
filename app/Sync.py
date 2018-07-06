import sys
import os
import subprocess
import json
from collections import OrderedDict

#python superScript.py "/home/downloads/Anime/[HorribleSubs] Just Because! - 08 [720p].mkv" "3A4038BF315EC6AE99FA073DFBF1702CEE412EF0" "[HorribleSubs] Just Because! - 08 [720p].mkv"
#python synckkk.py "/home/downloads/Anime/Mr.Robot.S03E10.720p.HDTV.x264-KILLERS[rarbg]" "Mr.Robot.S03E10.720p.HDTV.x264-KILLERS[rarbg]"

def readJson():
	json_data=open("ani-script/app/vars.json").read()
	data = json.loads(json_data, object_pairs_hook=OrderedDict)
	return data #an OrderedDict

settings = readJson()
os.chdir(settings['System Settings']['script_location'])

arg1 = sys.argv[1]
arg2 = sys.argv[2]
arg3 = sys.argv[3]

try:
    command = 'python3.5 Core/SyncShow.py \'' + arg1 + '\' \'' + arg3 + '\''
    process = subprocess.call(command, shell=True)
except Exception as e:
    print ("Failed to sync white show")

try:
	command = 'python3.5 Core/SyncAnime.py \'' + arg1 + '\' \'' + arg2 + '\' \'' + arg3 + '\''
	process = subprocess.call(command, shell=True)
except Exception as e:
	print (e)
	print ("Failed to sync anime")
