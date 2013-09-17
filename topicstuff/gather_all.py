#!/usr/bin/env python
from topic_classify import get_topics_and_words
import json
import os
import mechanize, cookielib


def gather_topics():

    br = mechanize.Browser()
    br.set_handle_robots(False)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_debug_http(True)
    br.set_debug_redirects(True)
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)
    global keep_going
    f = open('topics.txt', 'r')
    topics = json.loads( f.read() )['topics']
    f.close()
    try:
        f2 = open('not_crawled.txt', 'r')
        not_crawled = json.loads( f2.read() )
    except IOError:
        not_crawled = None
    if not_crawled != None:
        dont_crawl = not_crawled['topics']
    else:
        dont_crawl = None
    crawled = [i.split('.')[0] for i in os.listdir('topstructs')]
    to_crawl = [ topic for topic in topics if topic not in crawled ]
    if dont_crawl != None:
        to_crawl += [ topic for topic in topics if topic not in dont_crawl ]
   
    if len(to_crawl) > 0: 
        for topic in to_crawl:
            get_topics_and_words2(topic, dont_crawl, br)
    else:
        keep_going = False


if __name__ == '__main__':
    keep_going = True
    while keep_going:
        gather_topics()
    print "All Topics Gathered"
        
