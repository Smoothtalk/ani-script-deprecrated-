from setuptools import setup

setup(name='ani-script',
      version='0.0.1',
      description='Poorly coded rsync tranfer with mal database',
      url='https://github.com/Smoothtalk/ani-script/',
      author='Smoothtalk',
      license='MIT',
      packages=find_packages(exclude=['tests'])
      install_requires=[
          'discord.py',
          'bs4',
          'beautifulsoup4',
          'feedparser',
          'fuzzywuzzy',
          'python-Levenshtein',
          'simplejson',
          "urllib.error",
          "urllib.request",
          'trakt',
      ],
      )
