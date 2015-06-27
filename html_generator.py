#!/usr/bin/env python
# coding=utf-8

# Local imports
from config import DBPATH, LINKEXPIRE, LINKFRESH, OUTPUTDIR, \
                   ARTICLES_FRONT, SOURCE_URLS, DISQUS
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
from math import log
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
    
def get_mean_score(articles, penalize_length = True):
    """
    Returns the mean score per site, for normalization purposes.
    May use a term for length penalization, increasing the median
    value by log(number_articles) per site. In effect, that causes
    that sites that publish more quantity need also more quality
    to appear at the top of the ranking. True by default.
    """
    sites_score = {}
    for x in articles:
        url = x[1]
        site = get_top_level(url)
        if not site in sites_score:
            sites_score[site] = [x[3]]
        else:
            sites_score[site] += [x[3]]
    
    # Compute the average
    for k in sites_score:
        mean = sum(sites_score[k]) / float(len(sites_score[k]))
        if penalize_length:
            sites_score[k] = mean * log(len(sites_score[k]))
        else:
            sites_score[k] = mean
            
    return(sites_score)
    
def get_name(names, url):
    """
    Return the source name from the names dictionary using the url,
    or the top-level domain if not present in the dictionary. This
    function is used to ensure that the HTML page can be generated,
    even after changing SOURCE_URLS in a way that old articles in the
    database do not match any of the current source names.
    """
    site = get_top_level(url)
    if site in names:
        return names[site]
    else:
        return site

def get_age_modifier(age):
    """
    Returns a linear score modifier depending on the age of the link. 
    """
    if age < LINKFRESH:
        return 1.0
    else:
        return (LINKEXPIRE - age + LINKFRESH) / float(LINKEXPIRE)

def get_pagefile_from_title(title):
    """
    Returns an filename in the form: words-from-the-article-title 
    in order to create pages for single articles for the commenting
    system.
    """
    title = title.lower()
    title = re.sub(r"[^a-z0-9 ]", "", title)
    title = title.replace(" ", "-")
    return("/pages/" + title + ".html")

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
    
    # Create a lookup table for the titles of the sources.
    names = dict((get_top_level(x[0]), x[2]) for x in SOURCE_URLS)
    
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
    
    articles.sort(key = lambda x: x[3], reverse = True)
    articles = articles[:ARTICLES_FRONT]
    
    # Normalize the score for presentation
    scores = [x[3] for x in articles]
    max_score = max(scores)
    for i in xrange(len(articles)):
        articles[i][3] = "%.1f %%" % (articles[i][3] / max_score * 100)
        
    template_values = {}
    links = [{"url": x[1], "title": x[2], \
              "sourcename": get_name(names, x[1]), \
              "score": x[3], "qtitle": x[2].replace(' ', '+'), \
              "singlepage": get_pagefile_from_title(x[2])[1:], \
               "d_ident": DISQUS + str(x[0])} \
              for x in articles]
    template_values['links'] = links
    template_values['DISQUS'] = DISQUS
    rendered_index = tindex.render(template_values)
    # Save to output dir
    f = open(OUTPUTDIR + "/index.html", "w")
    f.write(rendered_index.encode("utf-8"))
    f.close()
    # Copy the CSS file
    copyfile("styles/style.css", OUTPUTDIR + "/style.css")
    
    # Create individual pages.
    single_template_values = {}
    tpage = env.get_template('single_page.html')
    for entry in articles:
        single_template_values = entry[2]
        single_template_values = {"url": entry[1], 
                                  "title": entry[2], \
                                  "sourcename": get_name(names, entry[1]), \
                                  "score": entry[3], \
                                  "qtitle": entry[2].replace(' ', '+'), \
                                  "DISQUS": DISQUS, \
                                  "DISQUSID" : DISQUS + str(entry[0])}
        rendered_page = tpage.render(single_template_values)
        f = open(OUTPUTDIR + get_pagefile_from_title(entry[2]), "w")
        f.write(rendered_page.encode("utf-8"))
        f.close()
        
    
