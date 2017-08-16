#!/usr/bin/python
# -*- coding: utf-8 -*-

#Usage : ./lyricfinder.py /path/to/folder/containing/music

import os
import urllib
import sys
import mutagen
from bs4 import BeautifulSoup

def fileToSearchQuery(file):
    mutagen.File(file)
    tags = mutagen.id3.ID3(file)
    title = tags.get("TIT2")
    artist = tags.get("TPE1")
    #a little cleanup because manipulating tags around can fuck things up sometimes
    for tag in tags:
        if not tag.startswith("TIT2") and not tag.startswith("TPE1"):
            tags.delall(tag)
    tags.save()
    query = str(artist) + " " + str(title)
    query = query.translate(None, "'!:?,;.$#()[]-_\&")
    query = query.replace(" ", "+")
    return query

def setLyricsToFile(lyrics, file):
    mutagen.File(file)
    tags = mutagen.id3.ID3(file)
    tags.add(mutagen.id3.USLT(encoding=3, lang=u'eng', desc=u'', text=lyrics))
    tags.save()

def searchLyrics(query):
    engine = "https://search.azlyrics.com/search.php?q="
    searchlink = engine + query
    #print("Search link : " + searchlink)
    soup = BeautifulSoup(urllib.urlopen(searchlink), "lxml")
    soup = soup.find("div", "main-page")
    soup = soup.find("table")
    if soup != None:
        soup = soup.find("a", None)
        lyricslink = soup["href"]
        soup = BeautifulSoup(urllib.urlopen(lyricslink), "lxml")
        soup = soup.find("div", "main-page").find("div", "ringtone").find_next_sibling("div")
        lyrics = soup.getText()
        lyrics = lyrics.replace("\r", "").replace("\n\n", "\n")
        return lyrics

directory = sys.argv[1]
print("Downloading lyrics for directory " + directory)
for file in os.listdir(directory):
    if file.endswith(".mp3"):
        filepath = directory + str(file)
        #print("Filepath : " + filepath)
        query = fileToSearchQuery(filepath)
        #print("Query : " + query)
        lyrics = searchLyrics(query)
        if lyrics != None:
            setLyricsToFile(lyrics, filepath)
            #createLrcFile(lyrics, file, directory)
            print("Downloaded lyrics for " + file)
        else:
            print("No lyrics found for " + file)