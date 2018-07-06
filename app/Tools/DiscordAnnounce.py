import asyncio
import os
import discord
import json
import sys
from collections import OrderedDict

discordClient = discord.Client()
token = ''

def readJson():
	json_data=open("vars.json").read()
	data = json.loads(json_data, object_pairs_hook=OrderedDict)
	return data #an OrderedDict

async def announce():
	await discordClient.wait_until_ready()

	messagePayload = "```" + str(sys.argv[1]) + " successfully synced" + "```"

	messageRecipient = await discordClient.get_user_info(settings['Users'][sys.argv[2]]['discord_ID'])
	await discordClient.send_message(messageRecipient, messagePayload)

	await discordClient.logout()

@discordClient.event
async def on_ready():
	print('Logged in as')
	print(discordClient.user.name)
	print(discordClient.user.id)
	await announce()
	print('-------')

settings = readJson()
token = settings['Discord Announcer']['Token']
if(token != ''):
	discordClient.run(token)
else:
	sys.exit(0)
