# feel_good/spiders/web_crawler.py
import scrapy
import csv
import os
import json
import re
from collections import defaultdict

# Same stop words and tokenize from your build_index.py
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
    'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which',
    'who', 'when', 'where', 'why', 'how'
}

def tokenize(text):
    if text is None:
        return []
    words = re.findall(r'\b\w+\b', text.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]

class WebCrawler(scrapy.Spider):
    name = 'feel_good_crawler'
    
    # Class variables to track state across all requests
    seen_urls = set()
    inverted_index = defaultdict(list)
    documents = {}
    doc_id = 0
    
    async def start(self):
        csv_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'data', 
            'top_sites.csv'
        )
        
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            
            count = 0
            for row in reader:
                if count > 1000:
                    break
                
                domain = row[1].strip()
                url = f'https://{domain}'
                
                yield scrapy.Request(url, callback=self.parse)
                count += 1
    
    def parse(self, response):
        # Skip if already seen
        if response.url in self.seen_urls:
            print(f'Skipped seen url {response.url}')
            return
        
        self.seen_urls.add(response.url)
        
        # Extract data
        title = response.css('title::text').get()
        text = ' '.join(response.css('p::text').getall())
        
        # Store document metadata
        self.documents[self.doc_id] = {
            'url': response.url,
            'title': title
        }
        
        # Tokenize and build index
        title_tokens = tokenize(title)
        text_tokens = tokenize(text)
        all_tokens = title_tokens + text_tokens
        
        # Build inverted index with positions
        word_positions = defaultdict(list)
        for position, word in enumerate(all_tokens):
            word_positions[word].append(position)
        
        # Add to inverted index
        for word, positions in word_positions.items():
            self.inverted_index[word].append({
                'doc_id': self.doc_id,
                'tf': len(positions),
                'positions': positions
            })
        
        self.doc_id += 1
        
        if self.doc_id % 100 == 0:
            print(f'Indexed {self.doc_id} documents...')
            self.save_index()
        elif self.doc_id % 10 == 0:
            print(f"Indexed {self.doc_id} documents...")
        
        # Follow links
        for link in response.css('a::attr(href)').getall():
            if link and not link.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                yield response.follow(link, callback=self.parse)
    
    def closed(self, reason):
        """Called when spider finishes - save the index"""
        print(f'\nSpider finished! Indexed {self.doc_id} documents')
        print(f'Vocabulary size: {len(self.inverted_index)} unique words')
        self.save_index()
        
        
    def save_index(self):
        # Save index and documents
        index_path = os.path.join(os.path.dirname(__file__), '..', '..', 'index.json')
        docs_path = os.path.join(os.path.dirname(__file__), '..', '..', 'documents.json')
        
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(dict(self.inverted_index), f)
        
        with open(docs_path, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f)
        
        print(f'Saved index to {index_path}')
        print(f'Saved documents to {docs_path}')