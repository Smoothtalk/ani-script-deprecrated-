import sys
import os
import subprocess
import json
from collections import OrderedDict

#python superScript.py "/home/downloads/Anime/[HorribleSubs] Just Because! - 08 [720p].mkv" "3A4038BF315EC6AE99FA073DFBF1702CEE412EF0" "[HorribleSubs] Just Because! - 08 [720p].mkv"
#python synckkk.py "/home/seedbox/downloads/Anime/Tosh.0.S09E01.720p.HDTV.x264-MiNDTHEGAP[rarbg]" "Tosh.0.S09E01.720p.HDTV.x264-MiNDTHEGAP[rarbg]"

def readJson():
	json_data=open("vars.json").read()
	data = json.loads(json_data, object_pairs_hook=OrderedDict)
	return data #an OrderedDict

print(os.getcwd())
settings = readJson()
os.chdir(settings['System Settings']['script_location'])

arg1 = sys.argv[1]
arg2 = sys.argv[2]
arg3 = sys.argv[3]

# try:
#     command = 'python synckkk.py \'' + arg1 + '\' \'' + arg3 + '\''
#     process = subprocess.call(command, shell=True)
# except Exception as e:
#     print "Failed to sync white show"

try:
	command = 'python3.5 Core/AnimeSync.py \'' + arg1 + '\' \'' + arg2 + '\' \'' + arg3 + '\''
	process = subprocess.call(command, shell=True)
except Exception as e:
	print (e)
	print ("Failed to sync anime")
