import scrapy
from ..items import ArticleItem

class AcmSpider(scrapy.Spider):
    name = "acm"
    
    keywords = [
        'Blockchain', 'Deep Learning', 'Big Data'
    ]

    custom_settings = {
        'DOWNLOAD_DELAY': 10,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
        'SELENIUM_HEADLESS': False,
    }

    def start_requests(self):
        base_url = "https://dl.acm.org/action/doSearch?AllField={}"
        
        for keyword in self.keywords:
            url = base_url.format(keyword.replace(' ', '%20'))
            yield scrapy.Request(
                url, 
                callback=self.parse, 
                meta={
                    'keyword': keyword,
                    'selenium': True,
                    'wait_time': 15,
                    'wait_selector': '.search__item, .issue-item'
                }
            )

    def parse(self, response):
        keyword = response.meta['keyword']
        
        self.logger.info(f"Page title: {response.css('title::text').get()}")
        self.logger.info(f"URL: {response.url}")
        
        # Try multiple selectors
        articles = response.css('li.search__item, div.issue-item')
        if not articles:
            articles = response.css('.search-result, .search-result-item')
        if not articles:
            articles = response.css('div.issue-item__content-right')
        
        self.logger.info(f"Found {len(articles)} articles for {keyword}")
        
        if not articles:
            self.logger.warning(f"No articles found. Saving HTML for debugging...")
            with open(f'debug_acm_{keyword.replace(" ", "_")}.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            return

        for idx, article in enumerate(articles[:25]):
            item = ArticleItem()
            item['source'] = 'ACM'
            item['mot_cle_recherche'] = keyword
            
            # Title - get all text
            titre_parts = article.css('h5.issue-item__title a *::text, h5.issue-item__title a::text, .hlFld-Title *::text, .hlFld-Title::text').getall()
            item['titre'] = ' '.join([t.strip() for t in titre_parts if t.strip()])
            
            # Link
            rel_url = article.css('h5.issue-item__title a::attr(href)').get()
            if rel_url:
                item['lien'] = response.urljoin(rel_url) if not rel_url.startswith('http') else rel_url
            else:
                item['lien'] = None
            
            # Authors - deduplicate
            auteurs_raw = article.css('ul.rlist--inline li a::text, .author-name::text').getall()
            item['auteurs'] = list(dict.fromkeys([a.strip() for a in auteurs_raw if a.strip()]))
            
            # Year
            year_text = article.css('span.dot-separator span::text').get()
            if year_text:
                import re
                year_match = re.search(r'\b(19|20)\d{2}\b', year_text)
                item['annee'] = year_match.group(0) if year_match else None
            else:
                item['annee'] = None
            
            # Abstract - get all text
            abstract_parts = article.css('div.issue-item__abstract p::text, div.issue-item__abstract::text, .abstract::text').getall()
            item['abstract'] = ' '.join([a.strip() for a in abstract_parts if a.strip()])
            
            # Journal - get all text
            journal_parts = article.css('.epub-section__title *::text, .epub-section__title::text, .publication-title::text').getall()
            item['journal'] = ' '.join([j.strip() for j in journal_parts if j.strip()])
            
            if item.get('titre') and item.get('lien'):
                self.logger.info(f"[{idx+1}] Scraped: {item['titre'][:50]}...")
                yield item
            else:
                self.logger.warning(f"[{idx+1}] Skipped - Title: {bool(item.get('titre'))}, Link: {bool(item.get('lien'))}")
