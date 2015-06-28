# reranker
Adapted [rank-es](https://github.com/rinze/rank-es), proof of concept.

Or: can anyone easily create a news aggregator without any user around to score the news articles? And: can we add comments to this?

And: can we do it in a very, very easy way?

## Keep it simple

Only two scripts are needed: one to populate the database and another one to generate static HTML files.

* `retriever.py`: downloads the new articles from the sources and stores them into the database. It also moves expired links and scores the ones still alive.
* `html_generator.py`: 

That's it.

## Installation and usage

You will need the following Python modules: feedparser, jinja2, sqlite3, urllib2, json. You can install them locally on your user directory with the `--user` option if you use `pip`: `pip install --user module`. I think this is much more convenient than creating a full environment. This should also work on shared hostings (I am on [DreamHost](http://www.dreamhost.com) and works like a charm.)

1. `mkdir db`
2. `sqlite3 db/reranker.db < schema.sqlite3`, or any other DB file you want.
3. Copy `config-sample.py` to `config.py` and edit the relevant variables so that they reflect the actual paths in your system. Use full paths whenever possible.
4. `cron`

### Finding whether my sources use "link" or "id" (or any other tag)

It should not be very difficult. Let's try with [The Guardian](http://www.theguardian.com).

    import feedparser
    test = feedparser.parse("http://www.theguardian.com/international/rss")
    test['entries'][0]

And then simply inspect the output. This feed, for instance, uses both:

    [...]
    'guidislink': False,
    'id': u'http://www.theguardian.com/politics/2015/jun/28/theresa-may-tunisia-gunman-did-not-target-britons-andrew-marr',
    'link': u'http://www.theguardian.com/politics/2015/jun/28/theresa-may-tunisia-gunman-did-not-target-britons-andrew-marr',
    'links': [{'href': u'http://www.theguardian.com [...]


