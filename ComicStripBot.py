#!/usr/bin/python3

import praw
import random
import time
import re
import requests
import json

HOW_OFTEN_TO_CHECK_AND_CROSSPOST = 60 * 60 #3600 secs = 1 hour

#Reddit API Credentials
ID = ''
SECRET = ''
USERNAME = ''
PASSWORD = ''
reddit = praw.Reddit(client_id=ID,client_secret=SECRET,user_agent='User-Agent: ComicStripsBot (by /u/grtgbln)', username=USERNAME, password=PASSWORD)

JSON_DATA = ""

SUB_FROM = 'comics'
SUB_TO = 'ComicStrips'

def crosspostPRAW(p):
    p.crosspost(subreddit=SUB_TO)

def checkIfAtLeast24Hours(p, timeThreshold):
    if int(p.created_utc) <= timeThreshold: #if post was made before thr 24 hour threshold
        return True

def checkIfAlreadyPosted(checkLink): #checks against the 100 most recent posts on r/comicstrips. Should be enough to check if a post on r/comics has already been crossposted
    for p in JSON_DATA['data']:
        if p['url'] == checkLink: #if r/comics post found on r/comicstrips
            return True
            break
    return False

def getNewPostPRAW(numberHot, timeThreshold):
    global JSON_DATA
    JSON_DATA = requests.get('https://api.pushshift.io/reddit/submission/search/?subreddit=' + str(SUB_TO) + '&size=100').json() #Reddit shut down similar API endpoint from PRAW, using PushShift.io API to search
    for p in reddit.subreddit(SUB_FROM).hot(limit=numberHot):
        if (not checkIfAlreadyPosted("https://www.reddit.com" + str(p.permalink))) and (checkIfAtLeast24Hours(p, timeThreshold)):
            print('Crossposting https://www.reddit.com' + str(p.permalink) + "...")
            crosspostPRAW(p)
            break
        else:
            print("Skipping https://www.reddit.com" + str(p.permalink) + "...")

def main():
    epoch24HoursAgo = int(time.time()) - (60 * 60 * 24) #current time - 24 hours
    print("Grabbing and checking top r/comics posts...")
    getNewPostPRAW(30, epoch24HoursAgo) #gets the top [number] post from the "hot" section, which Reddit manages and is constantly changing. 30 top posts should be enough, based on how active r/comics is and how frequently the bot checks for a new post to crosspost.

while True:
    main()
    print("Sleeping for " + str(HOW_OFTEN_TO_CHECK_AND_CROSSPOST) + " seconds.")
    time.sleep(HOW_OFTEN_TO_CHECK_AND_CROSSPOST)
