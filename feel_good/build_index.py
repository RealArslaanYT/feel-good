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

def build_inverted_index(jsonlines_path):
    inverted_index = defaultdict(list)
    documents = {}
    
    doc_id = 0
    
    with open(jsonlines_path, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)

            documents[doc_id] = {
                'url': data['url'],
                'title': data['title']
            }
            
            title_tokens = tokenize(data.get('title', ''))
            text_tokens = tokenize(data.get('text', ''))
            
            all_tokens = title_tokens + text_tokens
            
            word_positions = defaultdict(list)
            for position, word in enumerate(all_tokens):
                word_positions[word].append(position)

            for word, positions in word_positions.items():
                inverted_index[word].append({
                    'doc_id': doc_id,
                    'tf': len(positions),
                    'positions': positions
                })
            
            doc_id += 1
            
            if doc_id % 100 == 0:
                print(f"Processed {doc_id} documents...")
    
    print(f"Finished! Indexed {doc_id} documents")
    print(f"Vocabulary size: {len(inverted_index)} unique words")
    
    return dict(inverted_index), documents

def save_index(inverted_index, documents, index_path='index.json', docs_path='documents.json'):
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(inverted_index, f)
    
    with open(docs_path, 'w', encoding='utf-8') as f:
        json.dump(documents, f)
    
    print(f"Saved index to {index_path}")
    print(f"Saved documents to {docs_path}")

if __name__ == '__main__':
    inverted_index, documents = build_inverted_index('output_deduped.jsonlines')
    
    save_index(inverted_index, documents)
    
    print(f"\nExample entries:")
    for word in list(inverted_index.keys())[:5]:
        print(f"'{word}': appears in {len(inverted_index[word])} documents")