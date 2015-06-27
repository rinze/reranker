# Full path to the DB file created with the schema.sqlite3 file.
# DBPATH = "/home/me/whatever/reranker/db/dbfile.db"
DBPATH = ""

# Expiration time for links, in seconds. 86400 = 1 day
LINKEXPIRE = 86400  

# Number of seconds for a link not to age
LINKFRESH = 7200 

# Number of articles in front page
ARTICLES_FRONT = 20

# Output directory for the static HTML files. Will be created
# (along with the necessary subdirectories) if it does not
# exist.
# OUTPUTDIR = "/home/me/whatever/reranker/output/"
OUTPUTDIR = ""

# URLs for the RSS sources to retrieve. It is a tuple of tuples with 3 elements:
# the RSS URL for that site, the tag for the link to the news article
# within the XML, and the name for that source.
# You might have to play a bit with feedparser.parse() in order to 
# find it for your particular sources. It will tipically be either 
# "link" or "id".
# SOURCE_URLS = (("http://www.nytimes.com/services/xml/rss/nyt/HomePage.xml", "id", "The New York Times"),
#                ("https://www.sciencenews.org/feeds/headlines.rss", "link", "Sciencenews"),
#                ("http://www.wired.com/feed/", "link", "Wired"),
#                ("https://firstlook.org/theintercept/feed/?rss", "link", "The Intercept"))
SOURCE_URLS = ""

# Your code for the Disqus comment block.
# DISQUS = "mysite"
DISQUS = ""

