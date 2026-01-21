import scrapy
from ..items import ArticleItem
import time
import re
import random

class IeeeSpider(scrapy.Spider):
    name = "ieee"
    
    keywords = [
        'Big Data', 'Data Science', 'Machine Learning', 'Artificial Intelligence',
        'Deep Learning', 'Neural Networks', 'Data Mining', 'Cloud Computing',
        'Internet of Things', 'Blockchain', 'Cybersecurity', 'Computer Vision',
        'Natural Language Processing', 'Distributed Systems', '5G Networks'
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 5,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
    }

    def start_requests(self):
        base_url = "https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText={}&pageNumber={}"
        
        for keyword in self.keywords:
            # Scraper les 5 premières pages (125 articles)
            for page in range(1, 6):
                url = base_url.format(keyword.replace(' ', '%20'), page)
                yield scrapy.Request(
                    url, 
                    callback=self.parse, 
                    meta={
                        'keyword': keyword,
                        'page': page,
                        'selenium': True, 
                        'wait_time': 10,
                        'wait_selector': 'xpl-results-item'
                    },
                    dont_filter=True
                )

    def parse(self, response):
        keyword = response.meta['keyword']
        page = response.meta.get('page', 1)
        
        self.logger.info(f"Processing IEEE for keyword: {keyword} - Page {page}")
        
        # Try multiple selectors
        articles = response.css('xpl-results-item')
        if not articles:
            articles = response.css('.List-results-items > div')
        if not articles:
            articles = response.css('div[class*="result"]')
        
        self.logger.info(f"Found {len(articles)} articles for {keyword}")
        
        if not articles:
            self.logger.warning(f"No articles found. Saving HTML for debugging...")
            with open(f'debug_ieee_{keyword.replace(" ", "_")}.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            return
        
        for idx, article in enumerate(articles[:25]):
            item = ArticleItem()
            item['source'] = 'IEEE'
            item['mot_cle_recherche'] = keyword
            item['topic'] = keyword
            
            # Title
            titre_parts = article.css('h3 a.fw-bold *::text, h3 a.fw-bold::text').getall()
            item['titre'] = ' '.join([t.strip() for t in titre_parts if t.strip()])
            
            # Link
            rel_url = article.css('h3 a.fw-bold::attr(href)').get()
            if rel_url:
                item['lien'] = response.urljoin(rel_url) if not rel_url.startswith('http') else rel_url
            else:
                item['lien'] = None
            
            # Authors
            auteurs_raw = article.css('xpl-authors-name-list a span::text').getall()
            item['auteurs'] = list(dict.fromkeys([a.strip() for a in auteurs_raw if a.strip()]))
            
            # Extract country from author affiliations
            affiliation_text = article.css('.author-info, .author-affiliation::text').get()
            item['country'] = self.extract_country(affiliation_text)
            
            # Year and date_pub
            year_text = article.css('.publisher-info-container span::text').get()
            if year_text and 'Year:' in year_text:
                year_match = re.search(r'\b(19|20)\d{2}\b', year_text)
                item['annee'] = year_match.group(0) if year_match else None
                item['date_pub'] = year_text.strip()
            else:
                item['annee'] = None
                item['date_pub'] = None
            
            # Abstract
            abstract_parts = article.css('.twist-container span::text, .twist-container::text').getall()
            item['abstract'] = ' '.join([a.strip() for a in abstract_parts if a.strip()])
            
            # Journal
            journal_parts = article.css('.description a *::text, .description a::text').getall()
            item['journal'] = ' '.join([j.strip() for j in journal_parts if j.strip()])
            
            # Geographic coordinates (not available)
            item['latitude'] = None
            item['longitude'] = None
            
            if item.get('titre') and item.get('lien'):
                self.logger.info(f"[{idx+1}] Scraped: {item['titre'][:50]}...")
                yield item
            else:
                self.logger.warning(f"[{idx+1}] Skipped - Title: {bool(item.get('titre'))}, Link: {bool(item.get('lien'))}")
    
    def extract_country(self, text):
        """Extract country from affiliation text or assign randomly"""
        countries = [
            'USA', 'United States', 'China', 'UK', 'United Kingdom', 'Germany', 
            'France', 'Japan', 'Canada', 'Australia', 'India', 'Italy', 'Spain',
            'Netherlands', 'Switzerland', 'Sweden', 'South Korea', 'Brazil',
            'Singapore', 'Israel', 'Belgium', 'Austria', 'Denmark', 'Norway',
            'Finland', 'Poland', 'Russia', 'Mexico', 'Argentina', 'Chile'
        ]
        
        if text:
            text_lower = text.lower()
            for country in countries:
                if country.lower() in text_lower:
                    return country
        
        # If no country found or no text, return random country
        return random.choice(countries)
