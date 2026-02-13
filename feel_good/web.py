from flask import Flask, request, render_template
from search import load_index, calculate_idf, search
from threading import Thread, Lock
import time

app = Flask(__name__)

QUERY_LIMIT = 200

index_lock = Lock()

inverted_index, documents = load_index()
idf = calculate_idf(inverted_index, len(documents))

@app.after_request
def set_csp(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    return response

def reload_index():
    global inverted_index, documents, idf

    print("Waiting for lock...")
    with index_lock:
        print("Lock acquired! Reloading index...")
        inverted_index, documents = load_index()
        idf = calculate_idf(inverted_index, len(documents))
        print(f"Index reloaded! Now have {len(documents)} documents.")

def auto_reload_index():
    while True:
        time.sleep(300)
        reload_index()

Thread(target=auto_reload_index, daemon=True).start()

@app.route('/')
def home():
    return render_template('search.html', doc_count=len(documents))

@app.route('/search')
def search_results():
    query = request.args.get('q', '')
    query = query[:QUERY_LIMIT]
    with index_lock:
        results = search(query, inverted_index, documents, idf, top_n=50)
    return render_template('results.html', query=query, results=results)
