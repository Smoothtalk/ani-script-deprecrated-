import sys
import os

def readJson():
	json_data=open("../vars.json").read()
	data = json.loads(json_data, object_pairs_hook=OrderedDict)
	return data #an OrderedDict

settings = readJson()
in_file = settings['script_location'] + '/Data/completed.txt'
homedir = os.environ['HOME']
hashes = open(in_file,'r').readlines()

for hash in hashes:
	command = homedir + "/bin/rtcontrol --cull --yes hash=" + hash.strip()
	os.system(command)
os.remove(in_file)
