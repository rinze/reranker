# reranker
Adapted [rank-es](https://github.com/rinze/rank-es), proof of concept.

Or: can anyone easily create a news aggregator without any user around to score the news articles? And: can we add comments to this?

## Installation

You will need the following Python modules: feedparser, jinja2, sqlite3, urllib2, json. You can install them locally on your user directory with the `--user` option if you use `pip`: `pip install --user module`. I think this is much more convenient than creating a full environment. This should also work on shared hostings (I am on [DreamHost](http://www.dreamhost.com) and works like a charm.)

1. `mkdir db`
2. `sqlite3 db/reranker.db < schema.sqlite3`, or any other DB file you want.
3. Copy `config-sample.py` to `config.py` and edit the relevant variables so that they reflect the actual paths in your system. Use full paths whenever possible.

