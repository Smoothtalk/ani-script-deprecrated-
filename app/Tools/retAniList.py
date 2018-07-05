import os
import sys
import codecs
import requests
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

username = sys.argv[1]
database = "Data/" + username + ".xml"

url = 'https://graphql.anilist.co'

listVariables = {
    'userName'  : username,
    'type'      : "ANIME",
}

animeListQuery = '''
query getAnimeList ($userName : String, $type : MediaType) {
  MediaListCollection (userName : $userName, type : $type) {
    lists{
        entries {
            media {
                title {romaji, english}
                status
                startDate {year,month,day}
                endDate {year,month,day}
                }
            progress
            }
        }
    }
}
'''

response = requests.post(url, json={'query': animeListQuery, 'variables': listVariables})

prettySoup = json.dumps(response.json()['data']['MediaListCollection']['lists'], indent=4)
output = codecs.open(database, 'wb', 'utf-8')
output.write(prettySoup)
output.close()
