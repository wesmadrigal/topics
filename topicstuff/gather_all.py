#!/usr/bin/env python
from topic_classify import get_topics_and_words
import json
import os


def gather_topics():
    global keep_going
    f = open('/home/wes/Documents/projects/topic_classifier/topicstuff/topics.txt', 'r')
    d = json.loads( f.read() )
    f.close()
    topics = d['topics']
    try:
        failed = open('/home/wes/Documents/projects/topic_classifier/topicstuff/failed.txt', 'r').read().split('\n')
        current = [ i.split('.')[0] for i in os.listdir('/home/wes/Documents/projects/topic_classifier/topicstuff/topstructs') ]
        not_there = [ topic for topic in topics if topic not in current and topic not in failed ]
        if len(not_there) > 0:
            get_topics_and_words(not_there)
        else:
            keep_going = False
    except:
        gather_topics()

if __name__ == '__main__':
    keep_going = True
    while keep_going:
        gather_topics()
    print "All Topics Gathered"
        
