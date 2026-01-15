from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

class SeleniumMiddleware:
    def __init__(self, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
        # Anti-détection supplémentaire
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument(f'--window-size={random.randint(1200, 1920)},{random.randint(800, 1080)}')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Scripts anti-détection avancés
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                window.chrome = {runtime: {}};
            '''
        })
        self.headless = headless

    @classmethod
    def from_crawler(cls, crawler):
        headless = crawler.settings.get('SELENIUM_HEADLESS', True)
        middleware = cls(headless)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def process_request(self, request, spider):
        if request.meta.get('selenium'):
            # Comportement humain: délai aléatoire avant de charger
            time.sleep(random.uniform(2, 5))
            
            self.driver.get(request.url)
            
            wait_selector = request.meta.get('wait_selector')
            wait_time = request.meta.get('wait_time', 10)
            max_captcha_wait = request.meta.get('max_captcha_wait', 60)
            
            # Attendre le chargement initial
            time.sleep(random.uniform(3, 6))
            
            # Accepter les cookies si présent
            try:
                cookie_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[id*="accept"], button[id*="consent"], .cookie-accept, #onetrust-accept-btn-handler')
                cookie_btn.click()
                spider.logger.info("✅ Cookies acceptés")
                time.sleep(2)
            except:
                pass
            
            # Détecter CAPTCHA
            page_source = self.driver.page_source.lower()
            captcha_detected = any(word in page_source for word in ['captcha', 'robot', 'verify you are human'])
            
            if captcha_detected:
                spider.logger.warning(f"\n{'='*70}")
                spider.logger.warning("⚠️  CAPTCHA DÉTECTÉ!")
                spider.logger.warning(f"URL: {request.url}")
                
                if not self.headless:
                    spider.logger.warning(f"Vous avez {max_captcha_wait} secondes pour résoudre le CAPTCHA...")
                    spider.logger.warning("Résolvez le CAPTCHA dans le navigateur, puis attendez...")
                    spider.logger.warning(f"{'='*70}\n")
                    
                    # Attendre que le CAPTCHA soit résolu (vérifier périodiquement)
                    start_time = time.time()
                    while time.time() - start_time < max_captcha_wait:
                        time.sleep(5)
                        current_source = self.driver.page_source.lower()
                        if not any(word in current_source for word in ['captcha', 'robot', 'verify you are human']):
                            spider.logger.info("✅ CAPTCHA résolu! Continuation...")
                            break
                    else:
                        spider.logger.error("❌ Timeout: CAPTCHA non résolu")
                else:
                    spider.logger.error("Mode headless: impossible de résoudre le CAPTCHA")
                    spider.logger.error("Utilisez SELENIUM_HEADLESS = False dans settings.py")
            
            # Simuler comportement humain: scroll
            try:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
                time.sleep(random.uniform(1, 2))
                self.driver.execute_script("window.scrollTo(0, 0);")
            except:
                pass
            
            if wait_selector:
                try:
                    WebDriverWait(self.driver, wait_time).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
                    )
                    spider.logger.info(f"Element '{wait_selector}' found")
                except:
                    spider.logger.warning(f"Timeout waiting for '{wait_selector}' on {request.url}")
            
            time.sleep(random.uniform(2, 4))
            
            return HtmlResponse(
                self.driver.current_url,
                body=self.driver.page_source,
                encoding='utf-8',
                request=request
            )

    def spider_closed(self):
        self.driver.quit()
