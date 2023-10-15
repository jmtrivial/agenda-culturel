#!/usr/bin/python3
# coding: utf-8

import requests
import hashlib
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

import json

class Event:

    name = "event"
    keys = ["start_time_formatted", 'start_timestamp', 'is_past', "name", "price_info", "cover_media_renderer", "event_creator", "id", "day_time_sentence", "event_place", "comet_neighboring_siblings"]

    def __init__(self, event):
        self.data = event

    def __str__(self):
        return self.data["name"]

    def find_event_in_array(array):
        if isinstance(array, dict):
            #print([k for k in array])
            if len(Event.keys) == len([k for k in Event.keys if k in array]):
                return Event(array)
            else:
                for k in array:
                    v = Event.find_event_in_array(array[k])
                    if v != None:
                        return v
        elif isinstance(array, list):
            for e in array:
                    v = Event.find_event_in_array(e)
                    if v != None:
                        return v
        return None


#url="https://www.facebook.com/events/ical/export/?eid=2294200007432315"
url="https://www.facebook.com/events/2294199997432316/2294200007432315/"
#url_cal = "https://www.facebook.com/events/ical/export/?eid=993406668581410"
#url="https://jmtrivial.info"

cachedir = "cache"
result = hashlib.md5(url.encode())
hash = result.hexdigest()

filename = os.path.join(cachedir, hash + ".html")

if os.path.isfile(filename):
    #print("Use cache")
    with open(filename) as f:
        doc = "\n".join(f.readlines())
else:
    print("Download page")

    options = Options()
    options.add_argument("--headless=new")
    service = Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    doc = driver.page_source
    driver.quit()

    dir = os.path.dirname(filename)
    if not os.path.exists(dir):
        os.makedirs(dir)
    with open(filename, "w") as text_file:
        text_file.write(doc)


soup = BeautifulSoup(doc)

for json_script in soup.find_all('script', type="application/json"):
    json_txt = json_script.get_text()
    json_struct = json.loads(json_txt)
    event = Event.find_event_in_array(json_struct)
    if event != None:
        print(event)
