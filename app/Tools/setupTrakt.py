import json
import trakt.core
from trakt import init
from collections import OrderedDict

def readJson():
	json_data=open("../vars.json").read()
	data = json.loads(json_data, object_pairs_hook=OrderedDict)
	return data #an OrderedDict

settings = readJson()

trakt.core.AUTH_METHOD = trakt.core.OAUTH_AUTH

my_client_id = settings['Trakt Settings']['client_id']
my_client_secret = settings['Trakt Settings']['secret_id']

for user in settings['Users']:
	tracktUserName = settings['Users'][user]['traktUserName']
	init(tracktUserName, client_id=my_client_id, client_secret=my_client_secret, store=True)
