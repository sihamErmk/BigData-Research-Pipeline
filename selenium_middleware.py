from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

class SeleniumMiddleware:
    def __init__(self, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Use webdriver-manager to handle ChromeDriver automatically
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    @classmethod
    def from_crawler(cls, crawler):
        headless = crawler.settings.get('SELENIUM_HEADLESS', True)
        middleware = cls(headless)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def process_request(self, request, spider):
        if request.meta.get('selenium'):
            self.driver.get(request.url)
            
            wait_time = request.meta.get('wait_time', 5)
            time.sleep(wait_time)
            
            return HtmlResponse(
                self.driver.current_url,
                body=self.driver.page_source,
                encoding='utf-8',
                request=request
            )

    def spider_closed(self):
        self.driver.quit()
