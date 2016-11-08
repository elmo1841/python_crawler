import os
import shutil
import sys
import fnmatch
import datetime
from time import sleep
import random
import re

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import requests.certs
import ssl
from ssl import SSLError

from urllib.error import HTTPError
from urllib.error import URLError
from bs4 import BeautifulSoup




class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)

session = requests.session()
session.mount('https://', MyAdapter())

currentTime = datetime.datetime.now().strftime('%m%d%Y%H%M%S')

word_set = set()
word_bank = set()

headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
            "Accept":"text/html,application/xhtml+xml,application/xml; q=0.9,image/webp,*/*;q=0.8"}

class Word:
    def __init__(self, name, occurance):
        self.name = name
        self.occurance = occurance
    def increment_occurance():
        self.occurance += 1


def getBSObj(URL):
    try:
        url = "http://www.indeed.com" + URL
        req = session.get(url)
        bsObj = BeautifulSoup(req.text, "html.parser")

    except (HTTPError, URLError, AttributeError, ssl.SSLError, TimeoutError, requests.exceptions.ConnectionError) as e:
        print("error reached retreiving bsObj object")
        print(e)
        return None

    return bsObj

def createOutsideLinkFile():
    outside_writer = open("outside_link_text.txt", 'w')
    return outside_writer

def searchForFiles(outside_writer):
    for path, dir, files in os.walk("../"):
            for name in files:
                if "outside.txt" in name:
                    full_path = os.path.join(path, name)
                    print('found: ' + path)
                    copy_reader = open(full_path, 'r')
                    copyFiles(copy_reader, outside_writer)

def copyFiles(copy_reader, outside_writer):
    lines = copy_reader.readlines()

    for line in lines:
        outside_writer.write(line)

def run():
    outside_writer = createOutsideLinkFile()
    searchForFiles(outside_writer)
    outside_writer.close()

# run()

def collectPages():
    print('collectpages')
    out_reader = open('outside_link_text.txt', 'r')
    out = out_reader.readlines()
    tag_write = open("outside_pages.txt", 'w')
    for link in out:
        bodyObj = getBSObj(link)
        tag_write.write(str(bodyObj.encode('utf8', 'ignore')))
    tag_write.close()

# collectPages()

def splitUpWords():
    print('splitUpWords')
    with open('outside_pages.txt','r') as page_reader:
        for line in page_reader:
            for word in line.split():
               searchForWordOccurance(word)

def searchForWordOccurance(word):
    print('searchForWordOccurance')
    if word not in word_set:
        print('not')
        new_word = Word(word, 1)
        word_bank.add(new_word)
        word_set.add(word)
    else:
        for stored_word in word_bank:
            if stored_word.name == word:
                stored_word.increment_occurance

# splitUpWords()

# word_list = open('word_list.txt', 'w')
# for stored_word in word_bank:
#     word_list.write(stored_word.name + ": " + str(stored_word.occurance) + '\n')
# word_list.close()

short_list = open('div_list.txt', 'w')
with open('word_list.txt','r') as page_reader:
    for line in page_reader:
        if '<div' in line:
            short_list.write(line)
