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

class SimpleEvent:

    def __init__(self, data):
        self.elements = {}

        for key in ["id", "start_timestamp", "end_timestamp"]:
            self.elements[key] = data[key] if key in data else None

        if "parent_event" in data:
            self.parent = SimpleEvent(data["parent_event"])


class Event:

    name = "event"
    keys = [
            ["start_time_formatted", 'start_timestamp', 
             'is_past', 
             "name", 
             "price_info", 
             "cover_media_renderer", 
             "event_creator", 
             "id", 
             "day_time_sentence", 
             "event_place", 
             "comet_neighboring_siblings"],
            ["event_description"]
    ]
    rules = {
        "event_description": { "description": ["text"]},
        "cover_media_renderer": {"image_alt": ["cover_photo", "photo", "accessibility_caption"], "image": ["cover_photo", "photo", "full_image", "uri"]},
        "event_creator": { "event_creator_name": ["name"], "event_creator_url": ["url"] },
        "event_place": {"event_place_name": ["name"] }
    }

    def __init__(self, i, event):
        self.fragments = {}
        self.elements = {}
        self.neighbor_events = None
        self.add_fragment(i, event)

    def add_fragment(self, i, event):
        self.fragments[i] = event

        for k in Event.keys[i]:
            if k == "comet_neighboring_siblings":
                self.get_neighbor_events(event[k])
            elif k in Event.rules:
                for nk, rule in Event.rules[k].items():
                    c = event[k]
                    for ki in rule:
                        c = c[ki]
                    self.elements[nk] = c
            else:
                self.elements[k] = event[k]


    def get_neighbor_events(self, data):
        self.neighbor_events = [SimpleEvent(d) for d in data]

    def __str__(self):
        return str(self.elements) + "\n Neighbors: " + ", ".join([ne.elements["id"] for ne in self.neighbor_events])

    def consolidate_current_event(self):
        if self.neighbor_events is not None and "id" in self.elements:
            id = self.elements["id"]
            for ne in self.neighbor_events:
                if ne.elements["id"] == id:
                    self.elements["end_timestamp"] = ne.elements["end_timestamp"]

    def find_event_fragment_in_array(array, event):
        if isinstance(array, dict):

            for i, ks in enumerate(Event.keys):
                if len(ks) == len([k for k in ks if k in array]):
                    if event is None:
                            event = Event(i, array,)
                    else:
                        event.add_fragment(i, array)
                else:
                    for k in array:
                        event = Event.find_event_fragment_in_array(array[k], event)
        elif isinstance(array, list):
            for e in array:
                event = Event.find_event_fragment_in_array(e, event)

        if event is not None:
            event.consolidate_current_event()
        return event


#url="https://www.facebook.com/events/ical/export/?eid=2294200007432315"
url="https://www.facebook.com/events/2294199997432316/2294200007432315/"
#url_cal = "https://www.facebook.com/events/ical/export/?eid=993406668581410"
#url="https://jmtrivial.info"

cachedir = "cache"
result = hashlib.md5(url.encode())
hash = result.hexdigest()

filename = os.path.join(cachedir, hash + ".html")

if os.path.isfile(filename):
    # print("Use cache")
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

event = None
for json_script in soup.find_all('script', type="application/json"):
    json_txt = json_script.get_text()
    json_struct = json.loads(json_txt)

    event = Event.find_event_fragment_in_array(json_struct, event)

print(event)

