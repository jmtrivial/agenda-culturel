from abc import ABC, abstractmethod

from django.db import models

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

import urllib.request
from django.core.files.uploadedfile import SimpleUploadedFile
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse
import os

from bs4 import BeautifulSoup

import json
from datetime import datetime



from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class Extractor:

    @abstractmethod
    def extract(url):
        pass

    def download(url):
        try:
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            service = Service("/usr/bin/chromedriver")

            driver = webdriver.Chrome(service=service, options=options)
            driver.get(url)
            doc = driver.page_source
            driver.quit()
            return doc
        except Exception as e:
            logger.error(e)
            return None


    def guess_filename(url):
        a = urlparse(url)
        return os.path.basename(a.path)

    def download_media(url):
        # first download file
        
        basename = Extractor.guess_filename(url)
        try:
            tmpfile, _ = urllib.request.urlretrieve(url)
        except:
            return None

        # if the download is ok, then create create the corresponding file object
        return SimpleUploadedFile(basename, open(tmpfile, "rb").read())




class ExtractorFacebook(Extractor):

    class SimpleFacebookEvent:

        def __init__(self, data):
            self.elements = {}

            for key in ["id", "start_timestamp", "end_timestamp"]:
                self.elements[key] = data[key] if key in data else None

            if "parent_event" in data:
                self.parent = ExtractorFacebook.SimpleFacebookEvent(data["parent_event"])


    class FacebookEvent:

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

        def get_element(self, key):
            return self.elements[key] if key in self.elements else None


        def get_element_datetime(self, key):
            v = self.get_element(key)
            return datetime.fromtimestamp(v) if v is not None else None

        def add_fragment(self, i, event):
            self.fragments[i] = event

            if ExtractorFacebook.FacebookEvent.keys[i] == ["start_timestamp", "end_timestamp"]:
                self.get_possible_end_timestamp(i, event)
            else:
                for k in ExtractorFacebook.FacebookEvent.keys[i]:
                    if k == "comet_neighboring_siblings":
                        self.get_neighbor_events(event[k])
                    elif k in ExtractorFacebook.FacebookEvent.rules:
                        for nk, rule in ExtractorFacebook.FacebookEvent.rules[k].items():
                            c = event[k]
                            for ki in rule:
                                c = c[ki]
                            self.elements[nk] = c
                    else:
                        self.elements[k] = event[k]


        def get_possible_end_timestamp(self, i, data):
            self.possible_end_timestamp.append(dict((k, data[k]) for k in ExtractorFacebook.FacebookEvent.keys[i]))


        def get_neighbor_events(self, data):
            self.neighbor_events = [ExtractorFacebook.SimpleFacebookEvent(d) for d in data]

        def __str__(self):
            return str(self.elements) + "\n Neighbors: " + ", ".join([ne.elements["id"] for ne in self.neighbor_events])

        def consolidate_current_event(self):
            if self.neighbor_events is not None and "id" in self.elements and "end_timestamp" not in self.elements:
                if self.neighbor_events is not None and "id" in self.elements:
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
                for i, ks in enumerate(ExtractorFacebook.FacebookEvent.keys):
                    if len(ks) == len([k for k in ks if k in array]):
                        seen = True
                        if event is None:
                                event = ExtractorFacebook.FacebookEvent(i, array)
                        else:
                            event.add_fragment(i, array)
                        # only consider the first of FacebookEvent.keys
                        break
                if not seen:
                    for k in array:
                        event = ExtractorFacebook.FacebookEvent.find_event_fragment_in_array(array[k], event, False)
            elif isinstance(array, list):
                for e in array:
                    event = ExtractorFacebook.FacebookEvent.find_event_fragment_in_array(e, event, False)

            if event is not None and first:
                event.consolidate_current_event()
            return event


        def build_event(self, url):
            from .models import Event

            image = self.get_element("image")
            local_image = None if image is None else Extractor.download_media(image)


            return Event(title=self.get_element("name"), 
                status=Event.STATUS.DRAFT,
                start_day=self.get_element_datetime("start_timestamp"),
                start_time=self.get_element_datetime("start_timestamp"),
                end_day=self.get_element_datetime("end_timestamp"),
                end_time=self.get_element_datetime("end_timestamp"),
                location=self.get_element("event_place_name"),
                description=self.get_element("description"),
                local_image=local_image,
                image=self.get_element("image"),
                image_alt=self.get_element("image_alt"),
                reference_urls=[url])


    def process_page(txt, url):

        fevent = None
        soup = BeautifulSoup(txt, "html.parser")
        for json_script in soup.find_all('script', type="application/json"):
            json_txt = json_script.get_text()
            json_struct = json.loads(json_txt)
            fevent = ExtractorFacebook.FacebookEvent.find_event_fragment_in_array(json_struct, fevent)

        if fevent is not None:
            logger.info("Facebook event: " + str(fevent))
            result = fevent.build_event(url)
            return [result]
            
        return None


class ExtractorAllURLs:


    def extract(url):
        logger.info("Run extraction")

        txt = Extractor.download(url)
        if txt is None:
            logger.info("Cannot download url")
            return None

        result = ExtractorFacebook.process_page(txt, url)

        if result is not None:
            return result
        else:
            logger.info("Not a Facebook link")

        # TODO: add here other extrators

        return None
