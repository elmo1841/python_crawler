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

#---------------------WRITTEN FOR THIS FILE-----------------------------#

def updateNextIndex(fileName, directory):
    writer = open(fileName, 'w')
    writer.write(directory)
    writer.close()

def readIndex(fileName):
    reader = open(fileName, 'r')
    current = reader.read()
    reader.close()
    return current

def makeNewFile(directory, fileName):
    newFileName = directory + "/" + fileName + ".txt"
    if os.path.isfile(newFileName):
        newFile = open(newFileName, 'a')
    else:
        newFile = open(newFileName, 'w')
    return newFile

def makeNewDirectory(directory, extension):
    newDir = directory + "/" + extension
    if not os.path.exists(newDir):
        os.makedirs(newDir)
        newIndexWriter = makeNewFile(newDir, "index")
        newIndexWriter.write("0")
        newIndexWriter.close()
        newErrorWriter = makeNewFile(newDir, "errors")
        newIndexWriter.close()
    return newDir

def addToErrors(dir_name, error_link, e):
    print("error reached")
    errorWriter = makeNewFile(dir_name, "errors")
    errorWriter.write(error_link + "\n")
    errorWriter.write("{0}".format(err))
    errorWriter.close()

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

#steps that are called each in order
def stepZero():
    save = collectReferencedFolders("index_store/index_list.txt")
    archive = collectReferencedFolders("index_store/index_archive.txt")
    deleteOldFolders(save)

def collectReferencedFolders(list_name):
    return_set = set()

    index_reader = open(list_name, 'r')
    index = index_reader.readlines()

    for file_name in index:
        ref_file = readIndex(str(file_name).rstrip())
        return_set.add(ref_file)
        print(ref_file)

    index_reader.close()
    print("\n")
    return return_set

def deleteOldFolders(save):
    pattern = re.compile("^([0-9]{14})")

    for root, dir, files in os.walk("./"):
        for folder_name in dir:
            if pattern.match(str(folder_name)) and str(folder_name) not in save:
                shutil.rmtree(folder_name)

def stepOne(directory):
    index = readIndex("index_store/index_head.txt")
    if str(index) == "true":
        os.makedirs(directory)

        state_link_reader = open("state-links.txt", "r")

        search_var = ["table", "id", "cities", "^(\/l-)"]
        if_else_switch = [1, -1]

        traverseStateLinks(state_link_reader, directory, "cities", search_var, if_else_switch)

        updateNextIndex("index_store/index_state.txt", directory)

def traverseStateLinks(link_reader, work_dir, file_name, search_var, if_else_switch):
    links = link_reader.readlines()
    switch = if_else_switch[0]
    multiplier = if_else_switch[1]
    sub_dir = None
    sub_writer = None

    for link in links:
        if switch > 0:
            sub_dir = makeNewDirectory(work_dir, str(link).rstrip())
            sub_writer = makeNewFile(sub_dir, file_name)
        else:
            getStateLinks(link, sub_writer, sub_dir, search_var)
        switch *= multiplier

def getStateLinks(URL, link_writer, sub_dir, search_var):
    body = getBodyObj(URL, search_var)
    hrefRegex = search_var[3]
    try:
        for link in body.findAll("a", href=re.compile(hrefRegex)):
            fillCityLinks(link, link_writer)
    except (AttributeError, UnicodeEncodeError) as e:
        addToErrors(sub_dir, str(link), e)

    sleep(0.5)

def fillCityLinks(link, link_writer):
    link_text = str(link.getText().encode('utf8', 'ignore'))
    link_writer.write(link_text[2:] + "\r")
    new_link_text = decodeCityLink(link.attrs['href'])
    link_writer.write(new_link_text + "\r")

def decodeCityLink(link_text):
    i = 3
    x = link_text[i]
    while(x != ','):
        i += 1
        x = link_text[i]

    k = i + 2
    l = i + 4
    city_link = "/jobs?q=&l=" + link_text[3:i] + "%2C+" + link_text[k:l]
    return city_link

def stepTwo():
    directory = readIndex("index_store/index_state.txt")
    for root, dir, files in os.walk(directory):

            for state in dir:
                current_dir = root + "/" + state
                city_file = current_dir + '/cities.txt'
                city_reader = open(city_file, 'r')
                index = readIndex(current_dir + "/index.txt")

                search_var = ["td", "id", "resultsCol", "^(\/pagead\/clk\?)|(\/rc\/clk\?)|(&pp)"]
                if_else_switch = [1, -1]
                traverseCityLinks(city_reader, current_dir, "jobs", search_var, if_else_switch, index)
    updateNextIndex("index_store/index_city.txt", directory)

def traverseCityLinks(link_reader, work_dir, file_name, search_var, if_else_switch, index):
    head_index = 0;
    links = link_reader.readlines()
    cont_link = None
    switch = if_else_switch[0]
    multiplier = if_else_switch[1]
    sub_dir = None
    sub_writer = None

    if index != "complete":
        for link in links:
            if head_index < int(index):
                head_index += 1
            else:
                if switch > 0:
                    sub_dir = makeNewDirectory(work_dir, str(link).rstrip())
                    sub_writer = makeNewFile(sub_dir, file_name)
                else:
                    cont_link = getCityLinks(link, sub_writer, sub_dir, search_var)
                    while cont_link != None:
                        cont_link = getCityLinks(link, sub_writer, sub_dir, search_var)
                    head_index += 2
                    writeNewIndex(head_index, work_dir)
                switch *= multiplier
    writeNewIndex("complete", sub_dir)

def getCityLinks(URL, link_writer, sub_dir, search_attr):
    cont_link = None
    body = getBodyObj(URL, search_attr)
    hrefRegex = search_attr[3]
    try:
        for link in body.findAll("a", href=re.compile(hrefRegex)):
            if fillJobLinks(link, link_writer):
                cont_link = link.attrs['href']
    except (AttributeError, UnicodeEncodeError) as e:
        addToErrors(sub_dir, str(link), e)

    sleep(0.5)
    return cont_link

def fillJobLinks(link, link_writer):
    linkHREF = link.attrs['href']
    if "&pp" in linkHREF:
        return True
    else:
        link_writer.write(linkHREF + "\r")
        return False

def stepThree():
    directory = readIndex("index_store/index_city.txt")
    control = 0
    for root, dir, files in os.walk(directory):
        for city in dir:
            if control < 51:
                control += 1
            else:
                current_dir = root + "/" + city
                index = readIndex(current_dir + "/index.txt")
                jobs_file = current_dir + "/jobs.txt"
                job_crawler = open(jobs_file, 'r')
                traverseJobsLevelOne(job_crawler, current_dir, index)

def traverseJobsLevelOne(job_crawler, root, index):
    head_index = 0
    job_links = job_crawler.readlines()
    outside_file = root + "/outside.txt"
    outside_writer = open(outside_file, 'w')
    out_dir = makeNewDirectory(root, "outside")

    if index != "complete":
        if int(index) != 0:
            index = int(index) + 2
        for job in job_links:
            if head_index < int(index):
                print(head_index)
                head_index += 1
            else:
                retreiveJobUrl(job, index, outside_writer, root)
                head_index += 1
                writeNewIndex(head_index, root)
    writeNewIndex("complete", root)
    outside_writer.close()

def retreiveJobUrl(url, index, outside_writer, root):
    body_search_attr = ["table", "id", "job-content"]
    body = getBodyObj(url, body_search_attr)

    button_search_attr = ["span", "class", "indeed-apply-widget"]
    jobButton = getBodyObj(url, button_search_attr)

    view_link_attr = ["a", "class", "view_job_link"]
    link_view = getBodyObj(url, view_link_attr)

    if jobButton == None and link_view == None:
        goToOutside(url, index, outside_writer, root)
    else:
        if jobButton == None:
            pullIndeedJobDescription(url, index, root)
        else:
            try:
                jobId = jobButton.attrs['data-indeed-apply-jobid']
                if checkForDuplicateJob(jobId):
                    pullIndeedJobDescription(url, index, root)
                    jobIdSet.add(jobId)
            except (KeyError, UnicodeEncodeError, AttributeError) as e:
                addToErrors(sub_dir, str(url), e)
    sleep(0.5)

def pullIndeedJobDescription(url, index, root):
    bsObj = getBSObj(url)
    try:
        job_file = root + "/outside/" + str(index) + ".txt"
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

def goToOutside(url, index, outside_writer, root):

    job_file = root + "/" + str(index) + ".txt"
    job_write = open(job_file, 'w')
    try:
        bodyObj = getBSObj(url)
        classTags = bodyObj.findAll('div',{"class":True})
        for tag in classTags:
            class_attr = str(tag.attrs['class'])
            if 'job' in class_attr:
                job_write.write(tag.getText())

        idTags = bodyObj.findAll('div',{"id":True})
        for ids in idTags:
            id_attr = str(ids.attrs['id'])
            if 'job' in id_attr:
                job_write.write(ids.getText())
        job_write.write(link)
    except (KeyError, UnicodeEncodeError, AttributeError) as e:
        addToErrors(sub_dir, str(url), e)
    print(index)
    print("--------------------------------")
    job_write.close()






#beginning to end function calls
stepZero()
stepOne(currentTime)
stepTwo()
stepThree()


print("done")
