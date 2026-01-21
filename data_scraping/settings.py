BOT_NAME = 'data_scraping'

SPIDER_MODULES = ['data_scraping.spiders']
NEWSPIDER_MODULE = 'data_scraping.spiders'

ROBOTSTXT_OBEY = False

DOWNLOADER_MIDDLEWARES = {
    'data_scraping.selenium_middleware.SeleniumMiddleware': 800,
}

ITEM_PIPELINES = {
    'data_scraping.pipelines.MongoPipeline': 300,
}

MONGO_URI = 'mongodb://localhost:27017/'
MONGO_DATABASE = 'research_db'

DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 1

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'
FEED_EXPORT_ENCODING = 'utf-8'
