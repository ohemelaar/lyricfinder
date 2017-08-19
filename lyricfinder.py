#!/usr/bin/python3.5
# -*- coding: utf-8 -*-

#Usage : ./lyricfinder.py /path/to/folder/containing/musics

import os
import urllib
import sys
import mutagen
from bs4 import BeautifulSoup
from collections import namedtuple
from termcolor import colored

SearchResult = namedtuple("SearchResult", "desc link")

def fileToSearchQuery(file):
    mutagen.File(file)
    tags = mutagen.id3.ID3(file)
    title = tags.get("TIT2")
    artist = tags.get("TPE1")
    #a little cleanup because manipulating tags around can fuck things up sometimes
    #had to disable it because "RuntimeError: dictionary changed size during iteration"
    """
    for tag in tags:
        #for my personal use I remove all tags but title and artist
        if not tag.startswith("TIT2") and not tag.startswith("TPE1"):
            tags.delall(tag)
    tags.save()
    """
    query = str(artist) + " " + str(title)
    query = query.translate(str.maketrans(" ", "+", "'!:?,;.$#()[]-_\&"))
    return query

def setLyricsToFile(lyrics, file):
    mutagen.File(file)
    tags = mutagen.id3.ID3(file)
    tags.add(mutagen.id3.USLT(encoding=3, lang=u'eng', desc=u'', text=lyrics))
    tags.save()

def searchAZLyrics(query):
    engine = "https://search.azlyrics.com/search.php?q="
    searchlink = engine + query
    soup = BeautifulSoup(urllib.request.urlopen(searchlink), "lxml")
    soup = soup.find("div", "main-page")
    soup = soup.find("table")
    if soup is not None:
        desc = ' '.join(soup.find("td").getText().split())
        link = soup.find("a")["href"]
    else:
        desc = None
        link = None
    result = SearchResult(desc, link)
    return result

def extractAZLyrics(link):
    soup = BeautifulSoup(urllib.request.urlopen(link), "lxml")
    soup = soup.find("div", "main-page").find("div", "ringtone").find_next_sibling("div")
    lyrics = soup.getText()
    lyrics = lyrics.replace("\r", "").replace("\n\n", "\n")
    return lyrics

def searchWikia(query):
    engine = "http://lyrics.wikia.com/wiki/Special:Search?search="
    searchlink = engine + query
    soup = BeautifulSoup(urllib.request.urlopen(searchlink), "lxml")
    soup = soup.find("a", "result-link")
    if soup != None:
        desc = soup.getText()
        link = soup["href"]
    else:
        desc = None
        link = None
    result = SearchResult(desc, link)
    return result

def extractWikia(link):
    soup = BeautifulSoup(urllib.request.urlopen(link), "lxml")
    soup = soup.find("div", "lyricbox")
    lyrics = soup.getText()
    lyrics = lyrics.replace("\r", "").replace("\n\n", "\n")
    return lyrics

def isChoiceValid(choice):
    if len(choice) == 0:
        return False
    choice = choice[0]
    if "12nN".find(choice) != -1:
        return True
    else:
        return False

directory = sys.argv[1]
print("Downloading lyrics for directory " + directory)

for file in os.listdir(directory):
    if file.endswith(".mp3"):
        filename = file.replace(".mp3", "")
        filepath = directory + str(file)
        query = fileToSearchQuery(filepath)
        print("Song: " + filename)
        print("Do you want to search lyrics for this song?")
        print("")
        print(colored("y", "grey", "on_white", attrs=["bold"]) + "es/" + colored("s", "grey", "on_white", attrs=["bold"]) + "kip")

        #taking user input and checing it
        while True:
            choice = str(input(""))
            if len(choice) is not 0 and "yn".find(choice[0]) is not -1: break

        if choice[0] is "y":

            print("Searching Lyrics Wikia for " + filename)
            lyrically = searchWikia(query)

            if lyrically.link is None:
                print("No results found on Lyrics Wikia")
                print("search " + colored("m", "grey", "on_white", attrs=["bold"]) + "ore/" + colored("s", "grey", "on_white", attrs=["bold"]) + "top")

            else:
                print("")
                print("Result from Lyrics Wikia: " + colored(lyrically.desc, "green"))
                print("")
                print(colored("d","grey","on_white",attrs=["bold"]) + "ownload/search " + colored("m", "grey", "on_white", attrs=["bold"]) + "ore/" + colored("s", "grey", "on_white", attrs=["bold"]) + "top")

            #taking user input and checking it
            while True:
                choice = str(input(""))
                if lyrically.link is not None:
                    options = "dms"
                else:
                    options = "ms"
                if len(choice) is not 0 and options.find(choice[0]) is not -1: break

            if choice[0] is "d":
                lyrics = extractWikia(lyrically.link)
                setLyricsToFile(lyrics, filepath)
                print("Lyrics downloaded for " + filename)

            if choice[0] is "m":
                print("Searching AZLyrics for " + filename)
                azlyrics = searchAZLyrics(query)

                if azlyrics.link is None:
                    print("No lyrics found for " + filename)
                else:
                    print("")
                    print("Result from AZLyrics: " + colored(azlyrics.desc, "red"))
                    print("")
                    print(colored("d", "grey", "on_white", attrs=["bold"]) + "ownload/" + colored("s", "grey", "on_white", attrs=["bold"]) + "top")

                # taking user input and checing it
                while True:
                    choice = str(input(""))
                    if len(choice) is not 0 and "ds".find(choice[0]) is not -1: break

                if choice[0] is "d":
                    lyrics = extractAZLyrics(azlyrics.link)
                    setLyricsToFile(lyrics, filepath)
                    print("Lyrics downloaded for " + filename)