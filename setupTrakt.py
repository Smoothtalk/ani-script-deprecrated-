from trakt import init
import trakt.core
import json
from collections import OrderedDict

def readJson():
	json_data=open("vars.json").read()
	data = json.loads(json_data, object_pairs_hook=OrderedDict)
	return data #an OrderedDict

settings = readJson()

trakt.core.AUTH_METHOD = trakt.core.OAUTH_AUTH

my_client_id = settings['Trakt Settings']['client_id']
my_client_secret = settings['Trakt Settings']['secret_id']

init(settings['Users']["Smoothtalk"]['traktUserName'], client_id=my_client_id, client_secret=my_client_secret, store=True)
#init("Smoothtalk", client_id='31dc283b13ac16dc6e6f31fccfa0bbdeafbdf2db089c555b7b90ac581fd02daa', client_secret='55e1a69191ed9fd1339f26c41d245be50bec0ce22362645f1180535c14a15f82', store=True)
