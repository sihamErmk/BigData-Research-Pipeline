# Scrapy settings for research_scraper project

BOT_NAME = "research_scraper"

SPIDER_MODULES = ["spiders"] 
NEWSPIDER_MODULE = "spiders"

# Crawl responsibly
ROBOTSTXT_OBEY = False
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'

# Configure delays
DOWNLOAD_DELAY = 2
COOKIES_ENABLED = True

# Request headers
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Enable Selenium middleware for JavaScript-heavy sites
DOWNLOADER_MIDDLEWARES = {
    'selenium_middleware.SeleniumMiddleware': 800,
}

# Enable MongoDB pipeline
ITEM_PIPELINES = {
   'pipelines.MongoPipeline': 300,
}

# MongoDB settings
MONGO_URI = 'mongodb://localhost:27017/'
MONGO_DATABASE = 'research_db'

# Feed export
FEED_EXPORT_ENCODING = 'utf-8'

# Twisted reactor
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
