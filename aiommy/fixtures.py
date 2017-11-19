import datetime

from aiommy.dateutils import to_iso
from models import Event, FavoritePhoto, Photo, User

photo_keys = [
    '15834214258_26b1254bff_k.jpg',
    '16019680011_1ae9064d8d_k.jpg',
    '16020945192_808c82a8a7_k.jpg',
    '21450400064_b9d7fff873_k.jpg',
    '21452101763_f0e3026be6_k.jpg',
    '21885073460_a20b85e0f1_k.jpg',
    '22047108046_4b1ee1f95d_k.jpg',
    '22061460032_ced814354b_k.jpg',
    '22073722115_dd2a142441_k.jpg',
    '22083261081_9b0546722c_k.jpg',
    'GF-runners.jpg',
    'NAF16_pack_metzger-conley-rc-juan-erin_header.jpg',
    'Runners.jpg',
    'gifts-for-runners-1101446-TwoByOne.jpg',
    'lee12-aaacooldown2.jpg',
    'runners.jpeg',
    'shutterstock_105840977.jpg',
    'shutterstock_140614036-1-800x449.jpg',
]

event_urls = [f'{i + 1}.jpg' for i in range(10)]


def log_fixtures(model):
    def factory(method):
        def decorator(*args, **kwargs):
            print(f'[INFO] "{model.__name__}" data preparing')
            method(*args, **kwargs)
            print(f'[SUCCESS] "{model.__name__}" data has been created')
        return decorator
    return factory


@log_fixtures(User)
def create_user_fixtures(number=1):
    for i in range(number):
        User.create(username=f'username{i + 1}', password=f'password{i + 1}', provider='facebook')


def create_event_past_fixtures(number=50):
    events_past = (dict(
        name=f'Name{i}',
        location=f'Location{i}',
        start_date=to_iso(datetime.datetime.utcnow() - datetime.timedelta(days=(i % 50) * 365)),
        end_date=datetime.datetime.utcnow(),
        key=event_urls[i % len(event_urls)],
        lat=40.12345612,
        lon=38.65432112,
    ) for i in range(number))
    Event.insert_many(events_past).execute()


def create_event_upcoming_fixtures(number=50):
    events_upcoming = (dict(
        name=f'Name{i}',
        location=f'Location{i}',
        start_date=to_iso(datetime.datetime.utcnow() + datetime.timedelta(days=(i % 50) * 365)),
        end_date=datetime.datetime.utcnow(),
        key=event_urls[i % len(event_urls)],
        lat=40.123456,
        lon=38.6543211,
    ) for i in range(number))
    Event.insert_many(events_upcoming).execute()


@log_fixtures(Event)
def create_event_fixtures(number=50):
    create_event_past_fixtures(number)
    create_event_upcoming_fixtures(number)


@log_fixtures(Photo)
def create_photo_fixtures(number=40, events_number=100):
    photos = [[dict(
        key=photo_keys[i % len(photo_keys)],
        bibnumbers=f'{i} {i+1} {i+2}',
        owner=1,
        event=j+1,
    ) for i in range(number)] for j in range(events_number)]
    for photo_set in photos:
        Photo.insert_many(photo_set).execute()


@log_fixtures(FavoritePhoto)
def create_favorite_photo_fixtures(number=10, users_number=1):
    favorites = [[dict(
        photo=i + 1,
        owner=j + 1,
    ) for i in range(number)] for j in range(users_number)]
    for favorite_set in favorites:
        FavoritePhoto.insert_many(favorite_set).execute()


def create_fixtures():
    create_user_fixtures()
    create_event_fixtures()
    create_photo_fixtures()
    create_favorite_photo_fixtures()
