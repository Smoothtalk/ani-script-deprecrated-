#!/usr/bin/python

import sys
import os
import retMal
import linecache
import vars
import xml.etree.ElementTree as ET
import multiprocessing
from multiprocessing import Process

filePath = "/home/avi/Anime/[HorribleSubs] Kagewani S2 - 05 [480p].mkv"

seriesName = "Kagewani S2"
tempSeriesName = seriesName.replace(" ", "\ ")

command = "rsync --progress -v -z -e 'ssh -p" + vars.userport1 + "'" + " \"" + filePath + "\"" + ' ' + "\"" + vars.a_host + ":" + vars.remote_download_dir1 + "\""

print '\n'
print "Old Command:\n" + command

command = "rsync -aq --rsync-path='mkdir -p " + vars.remote_download_dir1 + tempSeriesName + "/ && rsync'" + " --progress -v -z -e 'ssh -p" + vars.userport1 + "'" + " \"" + filePath + "\"" + ' ' + "\"" + vars.a_host + ":" + vars.remote_download_dir1 + tempSeriesName + "/" + "\""

print '\n'
print "New Command:\n" + command

print '\n'
