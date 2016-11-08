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

headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
            "Accept":"text/html,application/xhtml+xml,application/xml; q=0.9,image/webp,*/*;q=0.8"}

jobIdSet = set()

def addToErrors(dir_name, error_link, e):
    print("error reached")
    # errorWriter = open(dir_name, "errors")
    # errorWriter.write(error_link + "\n")
    # errorWriter.write("{0}".format(err))
    # errorWriter.close()

def writeNewIndex(headIndex, work_dir):
    index_file = work_dir + "/index.txt"
    index_write = open(index_file, 'w')
    index_write.write(str(headIndex))
    print(headIndex)
    index_write.close()

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

def getBodyObj(URL, search_attr):
    tagType = search_attr[0]
    attrType = search_attr[1]
    attrName = search_attr[2]
    bsObj = getBSObj(URL)
    try:
        body = bsObj.find(tagType, {attrType:attrName})

    except (HTTPError, URLError, AttributeError, ssl.SSLError, TimeoutError, requests.exceptions.ConnectionError) as e:
        print("error reached retreiving url body object")
        print(e)
        return None

    return body

def stepThree():
    job_crawler = open("jobs.txt", 'r')
    current_dir = "."
    index = 0
    traverseJobsLevelOne(job_crawler, current_dir, index)

# TODO only changes below this line will go into working project
    # check for all index != 0 in complete.py

def traverseJobsLevelOne(job_crawler, root, index):
    head_index = 0
    job_links = job_crawler.readlines()
    outside_file = root + "/outside.txt"
    outside_writer = open(outside_file, 'w')

    if index != "complete":
        if int(index) != 0:
            index = int(index) + 2
        for job in job_links:
            if head_index < int(index):
                print(head_index)
                head_index += 1
            else:
                job_file = root + "/" + str(index) + ".txt"
                retreiveJobUrl(job, job_file, outside_writer, root)
                head_index += 1
                writeNewIndex(head_index, root)
    writeNewIndex("complete", root)
    outside_writer.close()

def retreiveJobUrl(url, job_file, outside_writer, sub_dir):
    body_search_attr = ["table", "id", "job-content"]
    body = getBodyObj(url, body_search_attr)

    button_search_attr = ["span", "class", "indeed-apply-widget"]
    jobButton = getBodyObj(url, button_search_attr)

    view_link_attr = ["a", "class", "view_job_link"]
    link_view = getBodyObj(url, view_link_attr)

    if jobButton == None and link_view == None:
        outside_writer.write(url)
    else:
        if jobButton == None:
            pullIndeedJobDescription(url, job_file, sub_dir)
        else:
            try:
                jobId = jobButton.attrs['data-indeed-apply-jobid']
                if checkForDuplicateJob(jobId):
                    pullIndeedJobDescription(url, job_file, sub_dir)
                    jobIdSet.add(jobId)
            except (KeyError, UnicodeEncodeError, AttributeError) as e:
                addToErrors(sub_dir, str(url), e)
    sleep(0.5)

def pullIndeedJobDescription(url, job_file, sub_dir):
    bsObj = getBSObj(url)
    try:
        job_write = open(job_file, 'w')
        for child in bsObj.find("span", {"id":"job_summary"}).children:
            writeText = child.getText().encode('utf16', 'ignore')
            job_write.write(child.getText())
        job_write.close()
    except (KeyError, UnicodeEncodeError, AttributeError) as e:
        addToErrors(sub_dir, str(url), e)

def checkForDuplicateJob(newJobId):
    if(newJobId in jobIdSet):
        return False
    else:
        return True

def oneTime():
    index = 0
    out_reader = open('outside.txt', 'r')
    out = out_reader.readlines()
    tag_write = open(str(index) + ".txt", 'w')
    for link in out:
        bodyObj = getBSObj(link)
        tag_write.write(str(bodyObj.encode('utf8', 'ignore')))
    tag_write.close()

def retreiveTags(tag, attribute, tag_write):
    tagsSet = bodyObj.findAll(tag,{attribute:True})
    for tag in tagsSet:
        tag_attr = str(tag.attrs[attribute])
        if 'job' in tag_attr or 'Job' in tag_attr:
            tag_write.write(tag.getText())

oneTime()
#stepThree()
