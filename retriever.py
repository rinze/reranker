#!/usr/bin/env python
# coding=utf-8

# Local imports
from config import DBPATH, LINKEXPIRE
# Global imports
import feedparser
import sqlite3
import urllib2
import json

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
    scores = fb, tw
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
    

if __name__ == "__main__":
    print get_score("http://elpais.com/")
    print old_link("http://www.nytimes.com")
