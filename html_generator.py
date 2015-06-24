#!/usr/bin/env python
# coding=utf-8

# Local imports
from config import DBPATH, LINKEXPIRE, LINKFRESH, OUTPUTDIR, \
                   ARTICLES_FRONT
# Library imports
from jinja2 import Environment, PackageLoader
import os
import sqlite3
import time
import dateutil.parser
import datetime
import calendar
from shutil import copyfile
from urlparse import urlparse
import re

__author__ = "José María Mateos"
__license__ = "GPL"

def get_articles():
    """
    Returns the articles currently in the database. Now that we are
    at it, it also returns the age of each article, in seconds, for
    the aging algorithm (a simple linear function), instead of the 
    original article date, which we won't need anymore at this point.
    Returns a list of [id, url, title, score, age].
    """
    conn = sqlite3.connect(DBPATH)
    c = conn.cursor()
    q1 = conn.execute("""SELECT id, url, title, score, datetime
                         FROM current""")
    rows = [list(x) for x in q1] # Get every entry into a list,
                                 # so it can be modified.
    now = time.mktime(datetime.datetime.utctimetuple(datetime.datetime.now()))
    # Put age instead of date.
    for i in range(len(rows)): 
        tmp1 = dateutil.parser.parse(rows[i][4])
        itemdate = calendar.timegm(tmp1.timetuple())
        age = now - itemdate
        rows[i][4] = age
    conn.close()
    return rows
    
def get_top_level(url):
    """
    Returns the top-level domain for this URL.
    For instance, well.blogs.nytimes.com -> nytimes.com.
    """
    domain = urlparse(url)
    domain = domain.netloc
    dots_idx = [m.start() for m in re.finditer('\\.', domain)]
    if (len(dots_idx) >= 2):
        return domain[dots_idx[-2] + 1:]
    else:
        return domain
    
def get_mean_score(articles):
    """
    Returns the mean score per site, for normalization purposes.
    """
    sites_score = {}
    sites_n = {}
    for x in articles:
        url = x[1]
        site = get_top_level(url)
        if not site in sites_score:
            sites_score[site] = 0
            sites_n[site] = 0
        else:
            sites_score[site] += x[3]
            sites_n[site] += 1
            
    # Compute the average
    for k in sites_score:
        sites_score[k] /= float(sites_n[k])
    return(sites_score)
    
def shorten_url(url, truncate = 50):
    """
    Shortened URL for aesthetic purposes.
    """
    if len(url) > truncate:
        return url[:truncate] + '...'
    else:
        return url

def get_age_modifier(age):
    """
    Returns a linear score modifier depending on the age of the link. 
    """
    if age < LINKFRESH:
        return 1.0
    else:
        return (LINKEXPIRE - age + LINKFRESH) / float(LINKEXPIRE)


if __name__ == "__main__":
    # Create the output dir if it does not exist.
    if not os.path.isdir(OUTPUTDIR):
        os.mkdir(OUTPUTDIR)
    # Create the output dir for the article pages, as well
    artdir = OUTPUTDIR + "/pages/"
    if not os.path.isdir(artdir):
        os.mkdir(artdir) 
    
    # Get the template for index.html
    env = Environment(loader = PackageLoader('html_generator', \
                                             'templates'))
    tindex = env.get_template('index.html')
    
    # Obtain the articles from the database and create a dictionary
    # with them after aging, factoring and sorting them so we have
    # a more or less coherent rank.
    articles = get_articles()
    means = get_mean_score(articles)
    for article in articles:
        age = article[4]
        url = article[1]
        agefactor = get_age_modifier(age)
        domain = get_top_level(url)
        article[3] = article[3] * agefactor / means[domain]
        # We can use a string here now
        article[3] = "%.4f" % article[3]
    
    articles.sort(key = lambda x: x[3], reverse = True)
    articles = articles[:ARTICLES_FRONT]
        
    template_values = {}
    links = [{"url": x[1], "title": x[2], \
              "surl": shorten_url(x[1]), \
              "score": x[3], "qtitle": x[2].replace(' ', '+')} \
              for x in articles]
    template_values['links'] = links
    rendered_index = tindex.render(template_values)
    # Save to output dir
    f = open(OUTPUTDIR + "/index.html", "w")
    f.write(rendered_index.encode("utf-8"))
    f.close()
    # Copy the CSS file
    copyfile("styles/style.css", OUTPUTDIR + "/style.css")
    
    # TODO: create individual pages
    
