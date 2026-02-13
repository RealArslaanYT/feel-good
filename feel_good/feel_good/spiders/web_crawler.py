import scrapy
import csv
import os
import json
import re
from collections import defaultdict

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
    
    seen_urls = set()
    inverted_index = defaultdict(list)
    documents = {}
    doc_id = 0
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_existing_index()
    
    def load_existing_index(self):
        index_path = os.path.join(os.path.dirname(__file__), '..', '..', 'index.json')
        docs_path = os.path.join(os.path.dirname(__file__), '..', '..', 'documents.json')
        
        if os.path.exists(index_path) and os.path.exists(docs_path):
            print("Loading existing index...")
            
            with open(index_path, 'r', encoding='utf-8') as f:
                loaded_index = json.load(f)
                self.inverted_index = defaultdict(list, loaded_index)
            
            with open(docs_path, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
            
            if self.documents:
                self.doc_id = max(int(k) for k in self.documents.keys()) + 1
            
            self.seen_urls = {doc['url'] for doc in self.documents.values()}
            
            print(f"Loaded {len(self.documents)} existing documents")
            print(f"Continuing from doc_id: {self.doc_id}")
            print(f"Already seen {len(self.seen_urls)} URLs")
        else:
            print("No existing index found, starting fresh")
        
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
                
                if url not in self.seen_urls:
                    yield scrapy.Request(url, callback=self.parse)
                else:
                    print(f"Skipping already-crawled root: {url}")
                
                count += 1
    
    def parse(self, response):
        if response.url in self.seen_urls:
            return
        
        self.seen_urls.add(response.url)
        
        title = response.css('title::text').get()
        text = ' '.join(response.css('p::text').getall())
        
        doc_id_str = str(self.doc_id)
        
        self.documents[doc_id_str] = {
            'url': response.url,
            'title': title
        }
        
        title_tokens = tokenize(title)
        text_tokens = tokenize(text)
        all_tokens = title_tokens + text_tokens
        
        word_positions = defaultdict(list)
        for position, word in enumerate(all_tokens):
            word_positions[word].append(position)

        for word, positions in word_positions.items():
            self.inverted_index[word].append({
                'doc_id': self.doc_id,
                'tf': len(positions),
                'positions': positions
            })
        
        self.doc_id += 1
        
        if self.doc_id % 100 == 0:
            print(f'Indexed {self.doc_id} documents (total)...')
            self.save_index()
        elif self.doc_id % 10 == 0:
            print(f"Indexed {self.doc_id} documents (total)...")
        
        for link in response.css('a::attr(href)').getall():
            if link and not link.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                absolute_url = response.urljoin(link)
                
                if absolute_url not in self.seen_urls:
                    yield scrapy.Request(absolute_url, callback=self.parse)
    
    def closed(self, reason):
        print(f'\nSpider finished! Total documents: {self.doc_id}')
        print(f'Vocabulary size: {len(self.inverted_index)} unique words')
        self.save_index()
        
    def save_index(self):
        index_path = os.path.join(os.path.dirname(__file__), '..', '..', 'index.json')
        docs_path = os.path.join(os.path.dirname(__file__), '..', '..', 'documents.json')
        
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(dict(self.inverted_index), f)
        
        with open(docs_path, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f)
        
        print(f'Saved index ({len(self.inverted_index)} terms, {len(self.documents)} docs)')