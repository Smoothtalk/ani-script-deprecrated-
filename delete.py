#!/usr/bin/python2.7

import sys
import os
import vars

in_file = vars.script_loc + "completed.txt"

hashes = open(in_file,'r').readlines()

for hash in hashes:
	command = "/home/seedbox/bin/rtcontrol --cull --yes hash=" + hash.strip()
	os.system(command)
os.remove(in_file)
