import os
import subprocess

dependencies = ['bs4', 'fuzzywuzzy']

def getList():
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
		rc = process.poll()

packages = getList()
theDependiciesLeft = checkList(packages)
if(len(theDependiciesLeft) == 0):
	print ("All Deps installed")
else:
	installMissingDependicies(theDependiciesLeft)
