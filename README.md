# feel good
a hobbyist search engine | made by [Arslaan Pathan](https://arslaancodes.com)

'feel good' is a custom search engine from scratch, using TF-IDF for rankings and scrapy for crawling. This was mainly created as a side project, don't expect it to be stable or for the search rankings to be very accurate. It is very much a work-in-progress/PoC, and was more of a way for me to learn web scraping than something actually made to be useful.

Live Demo: [https://feel-good.arslaancodes.com](https://feel-good.arslaancodes.com)

## Usage

1. Install requirements with `pip` from requirements.txt
2. In the "feel_good" directory, run `scrapy crawl feel_good_crawler --loglevel=WARNING`. This will crawl websites and save the inverted index and documents to `documents.json` and `index.json`.
3. Once you have enough documents/pages crawled (I recommend at least 5,000-10,000 to ensure better accuracy, but 1,000-2,000 is fine), stop the crawler with CTRL+C.
4. Get started by running a test search using the terminal. Make sure you are still in the `feel_good` directory and run `python3 search.py netflix`. You may replace 'netflix' with whatever search term you choose.
5. Run the web interface with `gunicorn -w 1 --threads 4 -b 0.0.0.0:8000 web:app`. Tweak the arguments as you like, it's just standard gunicorn.
