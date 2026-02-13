import json
import math
import sys
from collections import defaultdict
from build_index import tokenize

ARSLAAN_QUERIES = [
    'arslaan pathan',
    'arslaan',
    'arslaan p',
    'devwitharslaan',
    'arslaanpathan',
    'realarslaanyt',
]

def load_index(index_path='index.json', docs_path='documents.json'):
    with open(index_path, 'r', encoding='utf-8') as f:
        inverted_index = json.load(f)
    
    with open(docs_path, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    return inverted_index, documents

def calculate_idf(inverted_index, total_docs):
    idf = {}
    for term, postings in inverted_index.items():
        doc_freq = len(postings)
        idf[term] = math.log(total_docs / doc_freq)
    return idf

def search(query, inverted_index, documents, idf, top_n=10):
    query_tokens = tokenize(query)

    if not query_tokens:
        return []

    scores = defaultdict(float)

    for term in query_tokens:
        if term not in inverted_index:
            continue

        term_idf = idf[term]

        for posting in inverted_index[term]:
            doc_id = str(posting["doc_id"])
            tf = posting['tf']

            boost = 1
            if term in documents[doc_id]['title'].lower():
                boost *= 3
            if term in documents[doc_id]['url'].lower():
                boost *= 5
                
            scores[doc_id] += tf * term_idf * boost

    ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    results = []

    for doc_id, score in ranked_docs[:top_n]:
        results.append({
            'url': documents[doc_id]['url'],
            'title': documents[doc_id]['title'],
            'score': score
        })

    if query.lower().strip() == "feel good":
        sugarcrash_result = {
            'url': 'https://www.youtube.com/watch?v=JJnUiv61fFg',
            'title': 'ElyOtto - SugarCrash! (Visualiser) ft. Kim Petras, Curtis Waters',
            'score': 9999.99
        }
        results.insert(0, sugarcrash_result)
    
    if query.lower().strip() in ARSLAAN_QUERIES:
        arslaan_result = {
            'url': 'https://arslaancodes.com',
            'title': 'Arslaan Pathan | Home',
            'score': 9999.99
        }
        results.insert(0, arslaan_result)

    return results

def main():
    print("Loading index...")
    inverted_index, documents = load_index()
    total_docs = len(documents)
    print("Index loaded!")
    print(f"Total documents: {total_docs}")

    idf = calculate_idf(inverted_index, total_docs)

    try:
        query = ' '.join(sys.argv[1:])
    except IndexError:
        print("No query passed. Usage: python3 search.py <query>")
        sys.exit(1)
        
    results = search(query, inverted_index, documents, idf)
    
    if not results:
        print("No results found.\n")
        sys.exit(1)
    
    print(f"\nFound {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   {result['url']}")
        print(f"   Score: {result['score']:.2f}\n")

if __name__ == "__main__":
    main()