# !/usr/bin/env python
import json
import mechanize
import re
import cookielib

def get_topics_and_words(topics):
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
    all_struct = {"all_words": {}}
    #data = {"topic": {}, "all_words": {}}
    # initialize "all_words": {"count": 0}
    all_struct["all_words"]["count"] = 0
    # iteratively add words to this along the way and count
    # them each time they are encountered once again
    all_struct["all_words"]["words"] = {}
    # use the words in here when calculating to find out the amount of times they have
    # appeared in the document vs how many times they appeared in total
    for topic in topics:
        try:
            #data["topic"][topic] = {"words": {}, "documents": [], "total_words": 0}
            topic_struct = {"words": {}, "documents": [], "total_words": 0}
            #new_data = {"words": {}, "documents": [], "total_words": 0}
            seq = re.compile(r'[A-Za-z ]+[A-Za-z, ]+')
            api = 'http://www.jstor.org/action/doBasicSearch?Query={0}&Search=Search&gw=jtx&prq=topic+identifier&hp=100&acc=off&aori=off&wc=on&fc=off'
            br.open(api.format(topic))
            with_info = [i for i in br.links() if 'http://www.jstor.org/stable' in i.absolute_url]
            for link in with_info:
        
                br.follow_link(link)
                resp = br.response().read()
                if 'An abstract for this item is not available' not in resp:
                    start = resp.find('<div class="abstract">')
                    _next = resp.find('\n', resp.find('<p>', start+1)+1)
                    end = resp.find('</div>', _next+1)
                    text = resp[_next:end]
                    text = text[10:]
                    #data["topic"][topic]["documents"].append(text)
                    topic_struct["documents"].append(text)
                    words_list = re.findall(seq, text)
                    if words_list != None and len(words_list) > 0:
                        words_list = words_list[0].split(' ')
                        for word in words_list:
                            if word != '':
                                word = word.lower()
                                all_struct["all_words"]["count"] += 1
                                #data["topic"][topic]["total_words"] += 1
                                topic_struct["total_words"] += 1
                       
                                #f word not in data["all_words"]["words"].keys():
                                if word not in all_struct["all_words"]["words"].keys():
                                    # data["all_words"]["words"][word] = {"number": 1, "topics": [topic]}
                                    all_struct["all_words"]["words"][word] = {"number": 1}
                                else:
                                    # data["all_words"]["words"][word]["number"] += 1
                                    all_struct["all_words"]["words"][word]["number"] += 1
                                    #if topic not in data["all_words"]["words"][word]["topics"]:
                                    #    data["all_words"]["words"][word]["topics"].append(topic)
                                    #else:
                                    #    pass
                                #if word in data["topic"][topic]["words"].keys(): 
                                if word in topic_struct["words"].keys():
                                    #data["topic"][topic]["words"][word]["number"] += 1
                                    topic_struct["words"][word]["number"] += 1
                                else:
                                    topic_struct["words"][word] = {"number": 1}
                else:
                    pass
            f = open('/home/wes/Documents/projects/topic_classifier/topicstuff/topstructs/%s.txt' % topic, 'w')
            f.write( json.dumps( topic_struct )  )
            f.close()
        except:
            f = open('/home/wes/Documents/projects/topic_classifier/topicstuff/failed.txt', 'a')
            f.seek(0, os.SEEK_END)
            f.write('%s' % topic)
            f.close()
        
    ff = open('all_struct.txt', 'w')
    d = ff.write( json.dumps(all_struct) )
    ff.close()
    print "All topics finished and written"

# will need to be passed the list of topics so it can iterate through and build statistics for each of these

def get_probabilities(topics_list):
    #for topic in data["topic"].keys():
    for topic in topics_list:
        #total_for_topic = float(data["topic"][topic]["total_words"])
        # read in the topic structure that we created from above
        f = open('/home/wes/Documents/projects/topic_classifier/topicstuff/topstructs/%s.txt' % topic, 'r')
        d = json.loads( f.read() )
        f.close()
        total_for_topic = float( d["total_words"] )
        #for word in data["topic"][topic]["words"]:
        for word in d["words"].keys():
            #if "prob" not in data["topic"][topic]["words"][word].keys():
            if "prob" not in d["words"][word].keys():
                #words_count = float(data["topic"][topic]["words"][word]["number"])
                words_count = float( d["words"][word]["number"] )
                # total count of words
                prob = words_count / total_for_topic 
                #data["topic"][topic]["words"][word]["prob"] = prob
                d["words"][word]["prob"] = prob
            else:
                pass
    # rewrite the data to the file
        f = open('topstructs/%s.txt' % topic, 'w')
        f.write( json.dumps(d) )
        f.close()
        print "%s probabilities measured" % topic
    print "Probabilities for all words successfully weighed"


"""
    match_topic takes the data generated by get_topics_and_words and filtered through get_probabilities
    as parameters.  it then does the following...

    Calculate the probabilities using a Markov Chain to see P(T| w1, w2, ... wn) and selects the T
    based on the highest outcome of each topic's Markov Chained result.  The algorithm is smart enough
    to account for non-appearing words by assigning a probabilities of 1.0/total_words to the word that
    hasn't been observed conditioned on the pertinent topic
"""


def match_topic(topics_list, string):
    words = string.split()
    words = [ ''.join([e.lower() for e in word if e.isalpha()]) for word in words ]
    stats = {}
    # open the all struct
    all_struct = json.loads( open('all_struct.txt', 'r').read() )
    # assign an equal probability for each topic for ubiquity of probabilities
    #pt = 1.0/float( len(topics_list) )
    #for topic in data['topic'].keys():
    for topic in topics_list:
        topic_data = json.loads( open('topstructs/%s.txt' % topic, 'r').read() )
        stats[topic] = pt
        # for each word P(T| w)
        for word in words:
            #if word in data['topic'][topic]['words'].keys():
            if word in topic_data["words"].keys():
                #stats[topic] *= data['topic'][topic]['words'][word]['prob']
                stats[topic] *= topic_data["words"][word]['prob']
            # otherwise we will have to assign a probability to that word
            else:
                #stats[topic] *= 1.0 / float(data['all_words']['count'])
                stats[topic] *= 1.0 / float( all_struct['all_words']['count'] )
       
    return stats



 
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


def get_topics_and_words2(topic, dont_crawl, br):
    try:
        all_struct = json.loads( open('all_struct.txt', 'r').read() )
    except IOError:
        all_struct = {"all_words": {}}
        all_struct["all_words"]["count"] = 0
        # iteratively add words to this along the way and count
        # them each time they are encountered once again
        all_struct["all_words"]["words"] = {}
    # use the words in here when calculating to find out the amount of times they have
    # appeared in the document vs how many times they appeared in total
    topic_struct = {"words": {}, "documents": [], "total_words": 0}
    #new_data = {"words": {}, "documents": [], "total_words": 0}
    seq = re.compile(r'[A-Za-z ]+[A-Za-z, ]+')
    api = 'http://www.jstor.org/action/doBasicSearch?Query={0}&Search=Search&gw=jtx&prq=topic+identifier&hp=100&acc=off&aori=off&wc=on&fc=off'
    br.open(api.format(topic))
    with_info = [i for i in br.links() if 'http://www.jstor.org/stable' in i.absolute_url]
    try:
        for link in with_info:
        
            br.follow_link(link)
            resp = br.response().read()
            if 'An abstract for this item is not available' not in resp:
                start = resp.find('<div class="abstract">')
                _next = resp.find('\n', resp.find('<p>', start+1)+1)
                end = resp.find('</div>', _next+1)
                text = resp[_next:end]
                text = text[10:]
                #data["topic"][topic]["documents"].append(text)
                topic_struct["documents"].append(text)
                words_list = re.findall(seq, text)
                if words_list != None and len(words_list) > 0:
                    words_list = words_list[0].split(' ')
                    for word in words_list:
                        if word != '':
                            word = word.lower()
                            all_struct["all_words"]["count"] += 1
                            #data["topic"][topic]["total_words"] += 1
                            topic_struct["total_words"] += 1
                       
                            #f word not in data["all_words"]["words"].keys():
                            if word not in all_struct["all_words"]["words"].keys():
                                # data["all_words"]["words"][word] = {"number": 1, "topics": [topic]}
                                all_struct["all_words"]["words"][word] = {"number": 1}
                            else:
                                # data["all_words"]["words"][word]["number"] += 1
                                all_struct["all_words"]["words"][word]["number"] += 1
                                if word in topic_struct["words"].keys():
                                    #data["topic"][topic]["words"][word]["number"] += 1
                                    topic_struct["words"][word]["number"] += 1
                                else:
                                    topic_struct["words"][word] = {"number": 1}
            else:
                pass
    except:
        f = open('not_crawled.txt', 'w')
        if dont_crawl != None:
            dont_crawl.append(topic)
        else:
            dont_crawl = [topic]
        blob = {'topics': dont_crawl}
        f.write(json.dumps(blob))
        f.close()
        print "%s gave an error and we added to not crawl list" % topic

    f = open('/home/wes/Documents/projects/topic_classifier/topicstuff/topstructs/%s.txt' % topic, 'w')
    f.write( json.dumps( topic_struct )  )
    f.close()
        
    ff = open('all_struct.txt', 'w')
    d = ff.write( json.dumps(all_struct) )
    ff.close()
    print "All %s written and all_struct updated" % topic
