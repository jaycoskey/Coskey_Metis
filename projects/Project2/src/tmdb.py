#!/usr/bin/env python

import datetime
from functools import wraps
import json
import os
import requests
import sys
import time


DO_LOG = True
INTERVAL_SLEEP_TIME = 10
# ERRORS_MAX = 100
# MOVIES_MAX = 40
TMDB_API_KEY = os.environ['TMDB_API_KEY']
TMDB_MOVIE_ID_DATA_PATH = '../data/tmdb.org/movie_ids_01_21_2018.json'

def entering(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        print(f'Entering {f.__name__}')
        f(*args, **kwds)

# Sample line from movie_ids file:
#   {"adult":false,"id":3924,"original_title":"Blondie","popularity":0.170338,"video":false}
#
# @entering
def get_movie_objs(path):
    with open(path, 'r') as f:
        objs = [json.loads(line) for line in f.readlines()]
        objs_filtered = [obj for obj in objs if obj['adult'] == False]
        # objs_sorted = sorted(objs_filtered, key=lambda x: x['id'])
        # objs_sorted.reverse()
        return objs_filtered

# @entering
def get_movie_details_url(movie_id):
    return f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'

# @entering
def get_movie_keywords_url(movie_id):
    return f'https://api.themoviedb.org/3/movie/{movie_id}/keywords?api_key={API_KEY}'

# @entering
def log_details(movie_id):
    if not DO_LOG:
        return
    url = get_movie_details_url(movie_id)
    response = requests.get(url)
    assert(response.status_code == 200)
    content = response.text
    with open('details.json', 'a') as f:
        f.write(content + '\n')

# @entering
def log_details_errors(movie_id, e):
    if not DO_LOG:
        return
    ts = datetime.datetime.now()
    with open('details_errors.log', 'a') as f:
        f.write('{}: {}: {}\n'.format(
            ts.strftime('%Y-%m-%dT%H:%M:%S')
            , movie_id
            , str(e)
        ))

# @entering
def log_keywords(movie_id):
    if not DO_LOG:
        return
    url = get_movie_keywords_url(movie_id)
    response = requests.get(url)
    assert(response.status_code == 200)
    content = response.text
    with open('keywords.json', 'a') as f:
        f.write(content + '\n')

# @entering
def log_keywords_errors(movie_id, e):
    if not DO_LOG:
        return
    ts = datetime.datetime.now()
    with open('keywords_errors.log', 'a') as f:
        f.write('{}: {}: {}\n'.format(
            ts.strftime('%Y-%m-%dT%H:%M:%S')
            , movie_id
            , str(e)
        ))

def main():
    num_errors = 0
    num_movies = 0

    # ts = datetime.datetime.now()
    # print(f'ts={ts.strftime("%Y-%m-%dT%H:%M:%S")}')
    for movie_obj in get_movie_objs(TMDB_MOVIE_ID_DATA_PATH):
        # print(f'movie_obj={movie_obj}')
        # if num_errors > ERRORS_MAX:
        #     sys.exit(1)
        # if num_movies > MOVIES_MAX:
        #     sys.exit(2)
        movie_id = movie_obj['id']
        try:
        #    log_details(movie_id)
            log_keywords(movie_id)
        except Exception as e:
        #    log_details_errors(movie_id, e)
            log_keywords_errors(movie_id, e)
            num_errors += 1
        num_movies += 1
        if num_movies % 38 == 0:
            time.sleep(10)
    # ts = datetime.datetime.now()
    # print(f'ts={ts.strftime("%Y-%m-%dT%H:%M:%S")}')

main()

