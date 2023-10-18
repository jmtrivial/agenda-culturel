import os

from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger

from .extractors import ExtractorAllURLs 


# Set the default Django settings module for the 'celery' program.
APP_ENV = os.getenv("APP_ENV", "dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"agenda_culturel.settings.{APP_ENV}")

app = Celery("agenda_culturel")

logger = get_task_logger(__name__)


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def create_event_from_submission(self, url):
    from agenda_culturel.models import Event

    logger.info(f"{url=}")

    if len(Event.objects.filter(reference_urls__contains=[url])) != 0:
        logger.info("Already known url: ", url)
    else:
        try:
            logger.info("About to create event from submission")
            events = ExtractorAllURLs.extract(url)

            if events != None:
                for e in events:
                    e.save()

        except BadHeaderError:
            logger.info("BadHeaderError")
        except Exception as e:
            logger.error(e)


app.conf.timezone = "Europe/Paris"
