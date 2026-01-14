import scrapy
from items import ArticleItem
import xml.etree.ElementTree as ET

class ArxivSpider(scrapy.Spider):
    name = "arxiv"
    
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
        base_url = "http://export.arxiv.org/api/query?search_query=all:{}&start=0&max_results=25"
        
        for keyword in self.keywords:
            url = base_url.format(keyword.replace(' ', '+'))
            yield scrapy.Request(url, callback=self.parse, meta={'keyword': keyword})

    def parse(self, response):
        keyword = response.meta['keyword']
        
        self.logger.info(f"Processing arXiv for keyword: {keyword}")
        
        # Parse XML response
        try:
            root = ET.fromstring(response.text)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            entries = root.findall('atom:entry', ns)
            
            self.logger.info(f"Found {len(entries)} articles for {keyword}")
            
            for idx, entry in enumerate(entries):
                item = ArticleItem()
                item['source'] = 'arXiv'
                item['mot_cle_recherche'] = keyword
                
                # Title
                title_elem = entry.find('atom:title', ns)
                item['titre'] = title_elem.text.strip().replace('\n', ' ') if title_elem is not None else None
                
                # Link
                link_elem = entry.find('atom:id', ns)
                item['lien'] = link_elem.text.strip() if link_elem is not None else None
                
                # Authors
                authors = entry.findall('atom:author/atom:name', ns)
                item['auteurs'] = [author.text.strip() for author in authors if author.text]
                
                # Year - extract from published date
                published = entry.find('atom:published', ns)
                if published is not None and published.text:
                    # Format: 2024-01-15T10:30:00Z
                    year_text = published.text.strip()
                    item['annee'] = year_text[:4]  # Extract first 4 characters (year)
                else:
                    item['annee'] = None
                
                # Abstract
                summary = entry.find('atom:summary', ns)
                item['abstract'] = summary.text.strip().replace('\n', ' ') if summary is not None else None
                
                # Journal/Category
                categories = entry.findall('atom:category', ns)
                if categories:
                    item['journal'] = ', '.join([cat.get('term') for cat in categories if cat.get('term')])
                else:
                    item['journal'] = None
                
                if item.get('titre') and item.get('lien'):
                    self.logger.info(f"[{idx+1}] Scraped: {item['titre'][:50]}...")
                    yield item
                else:
                    self.logger.warning(f"[{idx+1}] Skipped - Title: {bool(item.get('titre'))}, Link: {bool(item.get('lien'))}")
                    
        except Exception as e:
            self.logger.error(f"Error parsing XML for {keyword}: {str(e)}")
            with open(f'debug_arxiv_{keyword.replace(" ", "_")}.xml', 'w', encoding='utf-8') as f:
                f.write(response.text)
