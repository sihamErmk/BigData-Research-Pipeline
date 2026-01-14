import scrapy
from items import ArticleItem
import time
import random

class ScienceDirectSpider(scrapy.Spider):
    name = "sciencedirect"
    
    # ⚠️ DÉSACTIVÉ - ScienceDirect bloque avec Cloudflare CAPTCHA
    # ✅ SOLUTION : Utilisez PyDoll (voir PYDOLL_GUIDE.md)
    keywords = ['Blockchain', 'Deep Learning', 'Big Data']  # Réactivé avec PyDoll

    custom_settings = {
        'DOWNLOAD_DELAY': 15,  # Augmenté
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
        'SELENIUM_HEADLESS': False,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'SELENIUM_WAIT_CAPTCHA': 120  # Attendre 2 minutes pour CAPTCHA manuel
    }

    def start_requests(self):
        base_url = "https://www.sciencedirect.com/search?qs={}"
        
        for idx, keyword in enumerate(self.keywords):
            url = base_url.format(keyword.replace(' ', '%20'))
            # Délai progressif entre les mots-clés
            if idx > 0:
                time.sleep(random.uniform(20, 30))
            
            yield scrapy.Request(
                url, 
                callback=self.parse, 
                meta={
                    'keyword': keyword, 
                    'pydoll': True,  # Utiliser PyDoll au lieu de Selenium
                    'wait_time': 15,
                    'max_captcha_wait': 120
                },
                dont_filter=True
            )

    def parse(self, response):
        keyword = response.meta['keyword']
        
        self.logger.info(f"Processing ScienceDirect for keyword: {keyword}")
        self.logger.info(f"Page title: {response.css('title::text').get()}")
        self.logger.info(f"URL: {response.url}")
        
        # Vérifier si CAPTCHA ou blocage
        page_text = response.text.lower()
        if 'captcha' in page_text or 'robot' in page_text or 'access denied' in page_text:
            self.logger.error(f"⚠️ CAPTCHA/BLOCAGE détecté pour {keyword}!")
            self.logger.error("Solutions:")
            self.logger.error("1. Résolvez le CAPTCHA manuellement dans le navigateur")
            self.logger.error("2. Attendez 5-10 minutes avant de réessayer")
            self.logger.error("3. Utilisez un VPN ou changez d'IP")
            self.logger.error("4. Essayez de scraper depuis un autre réseau")
            with open(f'captcha_sciencedirect_{keyword.replace(" ", "_")}.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            return
        
        # Try multiple selectors
        articles = response.css('div.result-item, article.js-article')
        if not articles:
            articles = response.css('ol.search-result-wrapper li')
        if not articles:
            articles = response.css('.ResultItem')
        if not articles:
            articles = response.css('li.js-article-result')
        
        self.logger.info(f"Found {len(articles)} articles for {keyword}")
        
        if not articles:
            self.logger.warning(f"No articles found. Saving HTML for debugging...")
            with open(f'debug_sciencedirect_{keyword.replace(" ", "_")}.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            return

        for idx, article in enumerate(articles[:25]):
            item = ArticleItem()
            item['source'] = 'ScienceDirect'
            item['mot_cle_recherche'] = keyword
            
            # Title
            item['titre'] = article.css('h2 a span::text, .result-list-title-link::text').get()
            if item['titre']:
                item['titre'] = item['titre'].strip()
            
            # Link
            rel_url = article.css('h2 a::attr(href)').get()
            if rel_url:
                item['lien'] = response.urljoin(rel_url) if not rel_url.startswith('http') else rel_url
            else:
                item['lien'] = None
            
            # Authors
            item['auteurs'] = [a.strip() for a in article.css('.author span::text').getall() if a.strip()]
            
            # Year
            year_text = article.css('.subtype-srctitle-date::text').get()
            if year_text:
                import re
                year_match = re.search(r'\b(19|20)\d{2}\b', year_text)
                item['annee'] = year_match.group(0) if year_match else None
            else:
                item['annee'] = None
            
            # Abstract
            item['abstract'] = article.css('.abstract-text::text').get()
            
            # Journal
            item['journal'] = article.css('.publication-title::text').get()
            
            if item.get('titre') and item.get('lien'):
                self.logger.info(f"[{idx+1}] Scraped: {item['titre'][:50]}...")
                yield item
            else:
                self.logger.warning(f"[{idx+1}] Skipped - Title: {bool(item.get('titre'))}, Link: {bool(item.get('lien'))}")
