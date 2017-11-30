import sys
import os
import json
from collections import OrderedDict

#python superScript.py "/home/downloads/Anime/[HorribleSubs] Just Because! - 08 [720p].mkv" "3A4038BF315EC6AE99FA073DFBF1702CEE412EF0" "[HorribleSubs] Just Because! - 08 [720p].mkv"

def readJson():
	json_data=open("vars.json").read()
	data = json.loads(json_data, object_pairs_hook=OrderedDict)
	return data #an OrderedDict

settings = readJson()
os.chdir(settings['System Settings']['script_location'])

arg1 = sys.argv[1]
arg2 = sys.argv[2]
arg3 = sys.argv[3]

sys.argv = ['synckkk.py', arg1, arg3]
execfile('synckkk.py')

sys.argv = ['sync.py', arg1, arg2, arg3]
execfile('sync.py')
