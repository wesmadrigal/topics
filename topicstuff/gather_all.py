#!/usr/bin/env python
from topic_classify import get_topics_and_words
import json
import os

if __name__ == '__main__':
    f = open('topics.txt', 'r')
    d = json.loads( f.read() )
    f.close()
    topics = d['topics']
    keep_going = True
    while keep_going:
        try:
            current = [ i.split('.')[0] for i in os.listdir('topstructs') ]
            not_there = [ topic for topic in topics if topic not in current ]
            if len(not_there) > 0:
                get_topics_and_words(not_there)
            else:
                keep_going = False
        except:
            pass
    print "Topic data acquired"
