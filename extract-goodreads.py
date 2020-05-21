import configparser
import os
import json
from betterreads import client

# string constant
NOT_SET_VALUE = 'NOT SET'

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
print(user.per_shelf_reviews())
