import os
import sys
import subprocess
import json
from collections import OrderedDict

baseFolder = '/ani-script/app'
homedir = os.environ['HOME']
noRtorrent = "The program \'rtorrent\' is currently not installed. You can install it by typing:\napt install rtorrent"
rtorrentAuto = '#system.method.set_key=event.download.finished,ascript,\"execute=python3.5,' + homedir + '/ani-script/app/Sync.py,$d.get_base_path=,$d.get_hash=,$d.get_name=\"'
cronTabData = "0,30 * * * * cd " + homedir + "/ani-script/app/Core && python3.5 PullAnime.py > /tmp/AnimePull.log\n5,35 * * * * cd " + homedir + "/ani-script/app/Core && python3.5 PullShow.py > /tmp/ShowPull.log\n0,0 * * * 0 cd " + homedir + "/ani-script/app/Tools && python3.5 DeleteFiles.py > /tmp/Delete.log\n5,0 * * * 0 cd " + homedir + "/downloads/Anime && find -size 0 -delete\n"

def checkRutorrent():
	try:
		process = subprocess.Popen(["rtorrent", "-h"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		while True:
			output = process.stdout.readline()
			error = process.stderr.readline()
			print ("Rtorrent found on system")
			os.chdir(os.path.expanduser('~'))
			lineInFile = False
			with open(".rtorrent.rc", "r") as ins:
				for line in ins:
					if line.strip() == rtorrentAuto.strip():
						lineInFile = True
			ins.close()

			if(lineInFile == False):
				ins = open(".rtorrent.rc", "a")
				ins.write(rtorrentAuto)
				ins.write('\n')
				ins.close()

			return
	except OSError as e:
		if e.errno == os.errno.ENOENT:
			print ("Rtorrent not installed")
		else:
			raise

def cronTabAdding():
	try:
		process = subprocess.Popen(["crontab", "-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		while True:
			output = process.stdout.readline()
			error = process.stderr.readline()
			noCronMessage = "b\'no crontab for " + str(homedir[6:] + '\'') #darn byte notation
			if str(error.strip()) == noCronMessage:
				tempCron = open("cron.tmp", "w+")
				tempCron.write(cronTabData)
				tempCron.close()
				process = subprocess.Popen(["crontab", "-u", homedir[6:], "cron.tmp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				output = process.stdout.readline()
				error = process.stderr.readline()
				os.remove("cron.tmp")
			else:
				cronList = cronTabData.split('\n')
				del cronList[4]
				process = subprocess.Popen(["crontab", "-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				tempCron = open("cron.tmp", "w+")
				#write output to file and then append the missing commands from remaining cronlist
				while True:
					output = process.stdout.readline()
					outputClean = str(output, 'utf-8')
					tempCron.write(outputClean)
					if outputClean == '' or outputClean == '\n':
						tempCron.close()
						break
					if output:
						for lines in cronList:
							if (str(output) == 'b\'' + lines + '\\n\''):
								cronList.remove(lines)

				if(len(cronList) == 0):
					pass
					print("All Crontab commands found")
					os.remove("cron.tmp")
				else:
					#one or more commands are missing
					tempCron = open("cron.tmp", "a+")
					for lines in cronList:
						tempCron.write(lines + '\n')
					tempCron.close()
					process = subprocess.Popen(["crontab", "-u", homedir[6:], "cron.tmp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
					output = process.stdout.readline()
					error = process.stderr.readline()
					os.remove("cron.tmp")
			break
	except OSError as e:
		print (type(e))
		if e.errno == os.errno.ENOENT:
			print ("File Not Found?")
		else:
			raise

def checkForRTcontrol():
	try:
		process = subprocess.Popen(["rtcontrol", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		while True:
			output = str(process.stdout.readline(), 'utf-8')
			error = str(process.stderr.readline(), 'utf-8')
			if (output != '' or error != ''):
				if "not found" in error:
					print ("Rtcontrol not found on system")
					print ("Please go to:\nhttp://pyrocore.readthedocs.io/en/latest/installation.html to install")
				else:
					#rtconrol Found
					pass
			else:
				break
	except OSError as e:
		print (type(e))
		if e.errno == os.errno.ENOENT:
			print ("File Not Found?")
		else:
			raise

def constructVarFile():
	if(not os.path.isfile(homedir + baseFolder + '/vars.json')):
		settings = {}
		users = {}
		systemSettings = {"script_location": "", "host_download_dir": "", "watch_dir": ""}
		traktSettings = {"client_id": "", "secret_id": ""}
		feedSettings = {"HS": "http://horriblesubs.info/rss.php?res=720", "UTW": "https://nyaa.si/?page=rss&c=1_2&f=1&u=Unlimited+Translation+Works"}
		number_of_users = input("How many users are using the script? ")
		try:
			for index in range(0, int(number_of_users)):
				userString = 'user' + str(index)
				user = {"remote_port": "22", "remote_host": "", "remote_download_dir": "", "traktUserName": "", "discord_ID": "", "custom_titles": []}
				users[userString] = user
		except OSError as e:
			print (type(e))
			if e.errno == os.errno.ENOENT:
				print ("File Not Found?")
			else:
				raise

		settings['Users'] = users
		settings['System Settings'] = systemSettings
		settings['Trakt Settings'] = traktSettings
		settings['Rss Feeds'] = feedSettings
		with open('vars.json', 'w') as fp:
			json.dump(settings, fp, indent=4)

def initalizeSSHKeys():
	os.chdir(homedir + "/ani-script/app")
	json_data=open("vars.json").read()
	settings=json.loads(json_data, object_pairs_hook=OrderedDict)

	for user in settings['Users']:
		if(settings['Users'][user]['remote_host'] != ""):
			try:
				host = str(settings['Users'][user]['remote_host'])
				port = str(settings['Users'][user]['remote_port'])
				command = "Tools/sshKeyGen.sh '" + host + "' '" + port + "'"
				os.system(command)

			except OSError as e:
				print (type(e))
				if e.errno == os.errno.ENOENT:
					print ("File Not Found?")
				else:
					raise

cronTabAdding()
checkRutorrent()
checkForRTcontrol()
constructVarFile()
initalizeSSHKeys()
