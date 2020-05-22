import configparser
import os
import json
from betterreads import client
import datetime

# string constant
NOT_SET_VALUE = 'NOT SET'
DATA_DIR = 'data'

def fix_book_json(book):
    keys_to_delete = []
    for key, value in book.items():
        if isinstance(value, dict):
            if '@type' in value:
                if value['@type'] == 'integer':
                    book[key] = int(value['#text'])
                else:
                    print(f"ERROR: missing converter for type: {value['@type']}")
            elif '@nophoto' in value:
                book[key] = value['#text']
            elif '@nil' in value:
                keys_to_delete.append(key)
        if key == 'authors':
            if 'image_url' in value['author']:
                value['author']['image_url'] = value['author']['image_url']['#text']
            if 'small_image_url' in value['author']:
                value['author']['small_image_url'] = value['author']['small_image_url']['#text']
    for key in keys_to_delete:
        del book[key]

    return book

config_parser = configparser.ConfigParser()
config_parser.read('config.ini')
client_key = config_parser.get('Client Parameters', 'client_key', fallback=NOT_SET_VALUE)
client_secret = config_parser.get('Client Parameters', 'client_secret', fallback=NOT_SET_VALUE)
access_token = config_parser.get('Client Parameters', 'access_token', fallback=NOT_SET_VALUE)
access_token_secret = config_parser.get('Client Parameters', 'access_token_secret', fallback=NOT_SET_VALUE)

gc = client.GoodreadsClient(client_key, client_secret)
if access_token == NOT_SET_VALUE:
    gc.authenticate()
else:
    gc.authenticate(access_token, access_token_secret)
 
access_token = gc.session.access_token
access_token_secret = gc.session.access_token_secret
config_parser['Client Parameters']['access_token'] = access_token
config_parser['Client Parameters']['access_token_secret'] = access_token_secret
with open('config.ini', 'w') as f:
    config_parser.write(f)

user = gc.user()
shelves = user.shelves()
return_value = { 'gid': user.gid, 'name': user.name, 'user_name': user.user_name, 'link': user.link, 'image_url': user.image_url, 'small_image_url': user.small_image_url, 'shelves': [] }
for shelf in shelves:
    shelf_dict = { 'count': shelf.count, 'description': shelf.description, 'exclusive': shelf.exclusive, 'featured': shelf.featured, 'gid': shelf.gid, 'name': shelf.name, 'sticky': shelf.sticky }
    reviews_objs = []
    reviews_page = 1
    reviews_for_page = user.per_shelf_reviews(shelf_name=shelf.name, page = reviews_page)
    reviews_objs.extend(reviews_for_page)
    while len(reviews_for_page) == 200:
        reviews_page += 1
        reviews_for_page = user.per_shelf_reviews(shelf_name=shelf.name, page = reviews_page)
        reviews_objs.append(reviews_for_page)
    reviews = []
    for review_obj in reviews_objs:
        review = { 'gid': review_obj.gid, 'book': fix_book_json(review_obj.book), 'rating': review_obj.rating, 'shelves': review_obj.shelves, 'comments_count': review_obj.comments_count, 'owned': review_obj.owned, 'url': review_obj.url  }
        if review_obj.recommended_for:
            review['recommended_for'] = review_obj.recommended_for
        if review_obj.recommended_by:
            review['recommended_by'] = review_obj.recommended_by
        if review_obj.body:
            review['body'] = review_obj.body
        if review_obj._review_dict['read_at']:
            review['read_at'] = review_obj.read_at.isoformat()
        if review_obj._review_dict['started_at']:
            review['started_at'] = review_obj.started_at.isoformat()
        reviews.append(review)
    
    shelf_dict['reviews'] = reviews
    return_value['shelves'].append(shelf_dict)

today = datetime.datetime.now().strftime("%Y-%m-%d")
with open( os.path.join(DATA_DIR, f'goodreads-{today}.json'), 'w') as f:
    json.dump(return_value, f, indent=2)
