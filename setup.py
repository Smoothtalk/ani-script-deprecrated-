from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(name='ani-script',
      version='0.0.1',
      description='Poorly coded rsync tranfer with mal database',
      url='https://github.com/Smoothtalk/ani-script/',
      author='Smoothtalk',
      license='MIT',
      packages=find_packages(exclude=['tests']),
      install_requires=[
      'discord.py',
      'bs4',
      'beautifulsoup4',
      'feedparser',
      'fuzzywuzzy',
      'python-Levenshtein',
      'simplejson',
      'trakt'
      ],
      )
