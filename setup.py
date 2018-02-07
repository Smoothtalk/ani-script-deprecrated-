import os
import subprocess

dependencies = ['bs4', 'fuzzywuzzy']
dependencies3 = ['discord.py', 'multidict', 'websockets']

def getPipList():
	try:
		packages = []
		process = subprocess.Popen(["sudo", "pip", "list", "--format=legacy"], stdout=subprocess.PIPE)
		while True:
			output = process.stdout.readline()
			if output != b'':
				package_Name = output[0:str(output).find(' ', 0)-2]
				package_Version = output[str(output).rfind(' '):len(str(output))-6].strip()
				#print ("name: " + str(package_Name) + " version: " + str(package_Version))
				installed_package = {'Name': str(package_Name).strip(), 'Version': str(package_Version).strip()}
				packages.append(installed_package)
			else:
				break
		return packages
	except OSError as e:
		print (type(e))
		if e.errno == os.errno.ENOENT:
			print ("File Not Found?")
		else:
			raise

def getPip3List():
	try:
		packages = []
		process = subprocess.Popen(["sudo", "pip3", "list", "--format=legacy"], stdout=subprocess.PIPE)
		while True:
			output = process.stdout.readline()
			if output != b'':
				package_Name = output[0:str(output).find(' ', 0)-2]
				package_Version = output[str(output).rfind(' '):len(str(output))-6].strip()
				#print ("name3: " + str(package_Name) + " version: " + str(package_Version))
				installed_package = {'Name': str(package_Name).strip(), 'Version': str(package_Version).strip()}
				packages.append(installed_package)
			else:
				break
		return packages
	except OSError as e:
		print (type(e))
		if e.errno == os.errno.ENOENT:
			print ("File Not Found?")
		else:
			raise

def checkList(packages):
	allPackageNames = []
	remainingDependicies = []
	index = 0

	for element in dependencies:
		remainingDependicies.append(element)

	for package in packages:
		allPackageNames.append(packages[index]['Name'])
		index+=1

	for term in dependencies:
		byteTerm = 'b\'' + term + '\'' #add binary typing ish
		if byteTerm in allPackageNames:
			remainingDependicies.remove(term)

	return remainingDependicies

def check3List(packages):
	allPackageNames = []
	remainingDependicies = []
	index = 0

	for element in dependencies3:
		remainingDependicies.append(element)

	for package in packages:
		allPackageNames.append(packages[index]['Name'])
		index+=1

	for term in dependencies3:
		byteTerm = 'b\'' + term + '\'' #add binary typing ish
		if byteTerm in allPackageNames:
			remainingDependicies.remove(term)

	return remainingDependicies

def installMissingDependicies(dependencies):
	failedToFind = b'No matching distribution found for'
	for package in dependencies:
		process = subprocess.Popen(["sudo", "pip", "install", package], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		while True:
			output = process.stdout.readline()
			error = process.stderr.readline()
			if(failedToFind in error):
				break
			if output == '' and process.poll() is not None:
				break
			if output:
				print (output.strip())
		rc = process.poll()

packages = getPipList()
packages3 = getPip3List()
theDependiciesLeft = checkList(packages)
theDependicies3Left = check3List(packages3)
if(len(theDependicies3Left) == 0):
	print ("All Deps of Pip3 installed")
else:
	installMissingDependicies(theDependicies3Left)
if(len(theDependiciesLeft) == 0):
	print ("All Deps of Pip installed")
else:
	installMissingDependicies(theDependiciesLeft)
