from abc import ABC, abstractmethod
#from .models import Event

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

import json


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

class ExtractorFacebook(Extractor):

    class FacebookEvent:

        name = "event"
        keys = ["start_time_formatted", 'start_timestamp', 'is_past', "name", "price_info", "cover_media_renderer", "event_creator", "id", "day_time_sentence", "event_place", "comet_neighboring_siblings"]

        def __init__(self, event):
            self.data = event

        def __str__(self):
            return self.data["name"]

        def find_event_in_array(array):
            if isinstance(array, dict):
                if len(ExtractorFacebook.FacebookEvent.keys) == len([k for k in ExtractorFacebook.FacebookEvent.keys if k in array]):
                    return ExtractorFacebook.FacebookEvent(array)
                else:
                    for k in array:
                        v = ExtractorFacebook.FacebookEvent.find_event_in_array(array[k])
                        if v != None:
                            return v
            elif isinstance(array, list):
                for e in array:
                        v = ExtractorFacebook.FacebookEvent.find_event_in_array(e)
                        if v != None:
                            return v
            return None

    def extract(url):
        txt = Extractor.download(url)
        if txt is None:
            logger.error("Cannot download " + url)
            return None
        else:
            soup = BeautifulSoup(txt, "html.parser")
            for json_script in soup.find_all('script', type="application/json"):
                json_txt = json_script.get_text()
                json_struct = json.loads(json_txt)
                fevent = ExtractorFacebook.FacebookEvent.find_event_in_array(json_struct)
                if fevent != None:
                    logger.info(str(fevent))
                    result = "TODO"
                    return result
        
        return None


class ExtractorAllURLs:


    def extract(url):
        logger.info("Run extraction")

        result = ExtractorFacebook.extract(url)

        if result is None:
            logger.info("Not a Facebook link")
            # add here other extrators
            pass

        return result
