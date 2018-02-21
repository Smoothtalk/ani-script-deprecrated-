#!/usr/bin/python

import os
import sys
import codecs
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

#flags
exists = '0'

if __name__ == "__main__":
    username = sys.argv[1]
    database = "Data/" + username + ".xml"

    url = 'http://myanimelist.net/malappinfo.php?u=' + username + '&status=watching&type=anime.xml'
    #url = 'https://currybox.ca/public/anime2.xml'
    #user_agent = 'api-indiv-7CFAF2BE04B34623771B356D83B38EC9'
    #headers = { 'User-Agent' : user_agent }

    flags = open('Data/flags', 'w')
    flags.write(exists)

    try:
        #req = urllib2.Request(url, None, headers)
        req = (url)
        response = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        if os.path.isfile(database):
            exists = '1'
            flags.write(exists)
    else:
        soup = BeautifulSoup(response.read(), "html.parser")
        soup2 = soup.prettify()

        output = codecs.open(database, 'wb', 'utf-8')
        output.write(soup2)
        output.close()

        with open(database, 'rt') as f:
            tree = ET.parse(f)

            for node in tree.findall('.//myinfo'):
                raw_user = node.find('user_name').text
                user = raw_user.strip()

                for node in tree.findall('.//anime'):
                    raw_title = node.find('series_title').text
                    raw_alt_title = node.find('series_synonyms').text
                    raw_status = node.find('my_status').text
                    raw_my_episodes = node.find('my_watched_episodes').text

                    title = raw_title.strip()
                    alt_title_unsplit = raw_alt_title.strip()
                    alt_title = alt_title_unsplit.split('; ')
                    status = raw_status.strip()

                    my_episodes = raw_my_episodes.strip()
            exists = '1'
            flags.write(exists)
    flags.close()
