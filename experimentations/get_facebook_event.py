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
            ["event_description"],
            ["start_timestamp", "end_timestamp"]
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
        self.possible_end_timestamp = []
        self.add_fragment(i, event)

    def add_fragment(self, i, event):
        self.fragments[i] = event

        if Event.keys[i] == ["start_timestamp", "end_timestamp"]:
            self.get_possible_end_timestamp(i, event)
        else:
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

    def get_possible_end_timestamp(self, i, data):
        self.possible_end_timestamp.append(dict((k, data[k]) for k in Event.keys[i]))

    def get_neighbor_events(self, data):
        self.neighbor_events = [SimpleEvent(d) for d in data]

    def __str__(self):
        return str(self.elements) + "\n Neighbors: " + ", ".join([ne.elements["id"] for ne in self.neighbor_events])

    def consolidate_current_event(self):
        if self.neighbor_events is not None and "id" in self.elements and "end_timestamp" not in self.elements:
            id = self.elements["id"]
            for ne in self.neighbor_events:
                if ne.elements["id"] == id:
                    self.elements["end_timestamp"] = ne.elements["end_timestamp"]
        
        if "end_timestamp" not in self.elements and len(self.possible_end_timestamp) != 0:
            for s in self.possible_end_timestamp:
                if s["start_timestamp"] == self.elements["start_timestamp"]:
                    self.elements["end_timestamp"] = s["end_timestamp"]
                    break

    def find_event_fragment_in_array(array, event, first = True):
        if isinstance(array, dict):

            seen = False
            for i, ks in enumerate(Event.keys):
                if len(ks) == len([k for k in ks if k in array]):
                    seen = True
                    if event is None:
                            event = Event(i, array)
                    else:
                        event.add_fragment(i, array)
                    # only consider the first of Event.keys
                    break
            if not seen:
                for k in array:
                    event = Event.find_event_fragment_in_array(array[k], event, False)
        elif isinstance(array, list):
            for e in array:
                event = Event.find_event_fragment_in_array(e, event, False)

        if event is not None and first:
            event.consolidate_current_event()
        return event


#url="https://www.facebook.com/events/ical/export/?eid=2294200007432315"
#url="https://www.facebook.com/events/2294199997432316/2294200007432315/"
#url="https://www.facebook.com/events/635247792092358/"
url="https://www.facebook.com/events/872781744074648"
url="https://www.facebook.com/events/1432798543943663?"
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

