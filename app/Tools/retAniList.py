import os
import sys
import codecs
import requests

url = 'https://graphql.anilist.co'

listVariables = {
    'userName' : "Myo",
    'type'   : "ANIME",
}


animeListQuery = '''
query getAnimeList ($userName : String, $type : MediaType) {
  MediaListCollection (userName : $userName, type : $type) {
    lists{
        entries {
            media {
                title {romaji, english}
                status
                }
            progress
            }
        }
    }
}
'''

response = requests.post(url, json={'query': animeListQuery, 'variables': listVariables})
print(response.json()['data']['MediaListCollection']['lists'])
