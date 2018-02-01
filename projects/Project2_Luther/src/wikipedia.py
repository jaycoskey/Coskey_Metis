#!/usr/bin/env python

from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
import requests
import sys
import time

def get_events_span(soup):
    h2_spans = [ span for h2 in soup.find_all('h2')
                 for span in h2.find_all('span') 
                 if span.string == 'Events'
               ]
    assert(len(h2_spans) == 1)
    events_span = h2_spans[0]
    return events_span


def get_event_stems(stemmer, stop_words, url):
    response = requests.get(url)
    assert(response.status_code == 200)
    content = response.text
    soup = BeautifulSoup(content, 'lxml')
    events_span = get_events_span(soup)
    event_text = get_event_text(events_span)

    empty_chars = ''.join(filter(lambda c: not c.isalpha() and not c.isspace(), event_text))
    translation = str.maketrans('-', ' ', empty_chars)
    event_stems = set([ get_stem(stemmer, word) for word in event_text.translate(translation).lower().split()
                    if word not in stop_words and len(word) > 2
                  ])
    return event_stems
    # print(' '.join(sorted(event_words)))
    # print(f'Stop words: {len(stop_words)}')
    print(f'Event words: {len(event_words)}')


def get_event_text(events_span):
    event_tags = []
    for event_tag in events_span.parent.next_siblings:
        # print(f'Name={event_tag.name}')
        if event_tag.name == 'h2':
            break
        if event_tag.name == 'h3':
            child0 = list(event_tag.children)[0]
            if child0.name == 'span' and child0.string == 'World population':
                break
        event_tags.extend(event_tag)
            
    event_tags = [event_tag for event_tag in event_tags if type(event_tag).__name__ == 'Tag']
    event_text = '\n'.join(map(lambda tag: tag.get_text(), event_tags))
    return event_text


def get_stem(stemmer, word):
    return stemmer.stem(word)


def main():
    stemmer = PorterStemmer()
    stop_words = []
    with open('../data/self/stopwords.txt', 'r') as f:
        stopwords = [word.lower() for line in f.readlines() for word in line.split()]
    for year in range(1875, 2018):
        time.sleep(5)
        url = 'https://en.wikipedia.org/wiki/' + str(year)
        stems = get_event_stems(stemmer, stop_words, url)
        filename_out = 'event_stems_' + str(year) + '.txt'
        with open(filename_out, 'w') as f:
            f.write(' '.join(stems))

main()

