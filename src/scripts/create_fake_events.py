from djipsum.faker import FakerModel
from agenda_culturel.models import Category, Event
import random
from datetime import datetime, timedelta

def run():

    tags = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
    tags = [w for w in tags.replace(",", "").replace(".", "").split() if len(w) >= 3]

    faker = FakerModel(app='agenda_culturel', model='Event')

    def random_hour():
        m = random.randint(0,59)
        h = random.randint(0,23)
        s = random.randint(0,59)
        return f'{h}:{m}:{s}'

    for j in range(20):
        sday = datetime.now() + timedelta(days=random.randint(0, 40))
        fields = {
            'title': faker.fake.text(max_nb_chars=100),
            'status': Event.STATUS.PUBLISHED,
            'category': faker.fake_relations(
                type='fk',
                field_name='category'
            ),
            'start_day': sday.date(),
            'location': faker.fake.text(max_nb_chars=100),
            'description': ' '.join(faker.fake.paragraphs()),
            'image': faker.fake.url(),
            'image_alt': faker.fake.text(max_nb_chars=100),
            'reference_urls': [faker.fake.url() for i in range(0, random.randint(0, 5))],
            'tags': [tags[random.randint(0, len(tags) - 1)] for i in range(0, random.randint(0, 10))]

        }
        if random.randint(0, 1) == 1:
            fields["start_time"] = random_hour()
        else:
            if random.randint(0, 5) == 1:
                fields["end_day"] = (sday + timedelta(days=random.randint(0, 6))).date()
                if random.randint(0, 1) == 1:
                    fields["end_time"] = random_hour()
        faker.create(fields)

