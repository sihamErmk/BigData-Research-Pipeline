import scrapy
from items import ArticleItem
import json

class ArxivSpider(scrapy.Spider):
    """Spider for arXiv.org - a free, open-access repository that doesn't block scrapers"""
    name = "arxiv"
    
    keywords = ['Blockchain', 'Deep Learning', 'Big Data']

    def start_requests(self):
        base_url = "http://export.arxiv.org/api/query?search_query=all:{}&start=0&max_results=10"
        
        for keyword in self.keywords:
            url = base_url.format(keyword.replace(' ', '+'))
            yield scrapy.Request(url, callback=self.parse, meta={'keyword': keyword})

    def parse(self, response):
        keyword = response.meta['keyword']
        
        # arXiv returns XML/Atom feed
        response.selector.remove_namespaces()
        entries = response.xpath('//entry')
        
        self.logger.info(f"Found {len(entries)} articles for keyword: {keyword}")
        
        for entry in entries:
            item = ArticleItem()
            item['source'] = 'arXiv'
            item['mot_cle_recherche'] = keyword
            item['titre'] = entry.xpath('.//title/text()').get()
            item['lien'] = entry.xpath('.//id/text()').get()
            
            authors = entry.xpath('.//author/name/text()').getall()
            item['auteurs'] = authors
            
            published = entry.xpath('.//published/text()').get()
            item['annee'] = published[:4] if published else None
            
            item['abstract'] = entry.xpath('.//summary/text()').get()
            item['journal'] = 'arXiv'
            
            if item['titre']:
                yield item
