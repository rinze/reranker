#!/usr/bin/env python
# coding=utf-8

# Local imports
from config import DBPATH, LINKEXPIRE
# Global imports
import feedparser
import sqlite3
import urllib2
import json
import time
import datetime
import dateutil.parse

__author__ = "José María Mateos"
__license__ = "GPL"

def get_score(url):
    """
    Return the url score according to both Facebook likes and Twitter
    shares. Only returns the aggregated score.
    """

    # Fix the URL and quote it
    try:
        url = urllib2.quote(fix_url(url))
    except:
        # This happens once in a while
        url = fix_url(url)

    # Get partial and global scores
    fb = get_fb_score(url)
    tw = get_tw_score(url)
    return fb+tw

def get_fb_score(url):
    """
    Returns Facebook score for the given url.
    Please note: http://stackoverflow.com/questions/5699270/how-to-get-share-counts-using-graph-api
    
    """

    try:
        fb_url = 'http://graph.facebook.com/' + url
        d = urllib2.urlopen(fb_url).read()
        j = json.JSONDecoder().decode(d)
        if 'shares' in j:
            return j['shares']
        else:
            return 0
    except:
        return 0
 
def get_tw_score(url):
    """
    Returns Twitter score for the given url.
    """

    try:
        tw_url = 'http://urls.api.twitter.com/1/urls/count.json?url=' \
                 + url
        d = urllib2.urlopen(tw_url).read()
        j = json.JSONDecoder().decode(d)
        return j['count']
    except:
        return 0

def fix_url(url):
    """
    Remove fragments (#) and add http:// if necessary.
    """

    # Remove the fragment, if present
    fragment = url.find('#')
    if fragment != -1:
        url = url[:fragment]

    if not url.startswith('http://') and \
       not url.startswith('https://'):
        return 'http://' + url.lower()
    else:
        return url.lower()

def old_link(url):
    """
    Returns True if the link is already present in the database,
    or False otherwise.
    """
    conn = sqlite3.connect(DBPATH)
    c = conn.cursor()
    # From active links
    q1 = c.execute("SELECT COUNT(*) FROM current WHERE url = ?", \
                  (url,))
    incurrent = q1.fetchone()[0]
    # From dead links
    q2 = c.execute("SELECT COUNT(*) FROM dead WHERE url = ?", \
                  (url,))
    indead = q2.fetchone()[0]
    conn.close()
    return (incurrent + indead > 0)
    
def parse_feed(feed, link_keyword):
    """
    Parses the given feed. Of all three sources used in this
    experiment, the only thing that changes between them is the
    keyword for the actual link, so this is passed as an argument
    """
    data = [(x[link_keyword], x["title"], \
             get_score(x[link_keyword]), \
             time.strftime("%Y-%m-%dT%H:%M:%SZ", \
                           x["published_parsed"])) \
             for x in feed["entries"]]
    return(data)
    
def get_expired_ids():
    """
    Return the ids for the links on the 'current' table that 
    have already expired.
    """
    
    now = datetime.datetime.utctimetuple(datetime.datetime.now())
    a = dateutil.parser.parse('2015-06-21T16:28:22Z')
    
if __name__ == "__main__":
    # For each source, create a list of (url, title, score, date)
    # tuples.
    
    # Source #1: New York Times
    print "Scoring New York Times...", 
    nyrss = "http://www.nytimes.com/services/xml/rss/nyt/HomePage.xml"
    nyfeed = feedparser.parse(nyrss)
    nydata = parse_feed(nyfeed, "id")
    nyscore = float(sum([x[2] for x in nydata])) / len(nydata)
    print "OK"

    # Source #2: Wired
    print "Scoring Wired...", 
    wrss = "http://www.wired.com/feed/"
    wfeed = feedparser.parse(wrss)
    wdata = parse_feed(wfeed, "link")
    wscore = float(sum([x[2] for x in wdata])) / len(wdata)
    print "OK"
    
    # Source #3: The Intercept
    print "Scoring The Intercept...",
    tirss = "https://firstlook.org/theintercept/feed/?rss"
    tifeed = feedparser.parse(tirss)
    tidata = parse_feed(tifeed, "link")
    tiscore = float(sum([x[2] for x in tidata])) / len(tidata)
    print "OK"

    # Compute normalization factors to account for the fact that 
    # different sites have different share / like scores.
    print "Normalizing...",
    scoresum = nyscore + wscore + tiscore
    nyfactor = scoresum / nyscore
    wfactor = scoresum / wscore
    tifactor = scoresum / tiscore

    # Normalise
    nydata = [(x[0], x[1], x[2] * nyfactor, x[3]) for x in nydata]
    wdata = [(x[0], x[1], x[2] * wfactor, x[3]) for x in wdata]
    tidata = [(x[0], x[1], x[2] * tifactor, x[3]) for x in tidata]
    print "OK"
    
    # We can work with everything together past this point
    items = nydata + wdata + tidata

    # Ok, time to work with the DB. First, filter out all the links
    # we already know, so we don't insert them twice
    print "Filtering out old links...",
    items = filter(lambda x: not old_link(x[0]), items)
    print "OK"

    # Expired links should be moved to the "dead" table. This is a
    # great moment for doing so.
    expired_ids = get_expired_ids()
    
