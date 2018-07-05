import os
import sys
import codecs
import requests
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

username = sys.argv[1]
database = "Data/" + username + ".json"

url = 'https://graphql.anilist.co'

listVariables = {
    'userName'  : username,
    'type'      : "ANIME",
}

animeListQuery = '''
query getAnimeList ($userName : String, $type : MediaType) {
  MediaListCollection (userName : $userName, type : $type) {
    lists{
        status
        entries {
            progress
            mediaId
            media {
                status
                synonyms
                title {romaji, english}
                startDate {year,month,day}
                endDate {year,month,day}
                }
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
