import requests
from bs4 import BeautifulSoup
import time
import os
import random
import re

URLS_FILE = "urls.txt"
OUTPUT_DIR = "docs/articles"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_article(url):
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # ArXiv specific selectors
            title_tag = soup.find('h1', class_='title')
            abstract_tag = soup.find('blockquote', class_='abstract')

            if not title_tag or not abstract_tag:
                # Fallback for meta tags?
                print(f"Skipping {url}: Could not parse title/abstract")
                return None, None

            title = title_tag.text.replace('Title:', '').strip()
            abstract = abstract_tag.text.replace('Abstract:', '').strip()
            return title, abstract
        else:
            print(f"Failed to fetch {url}: Status {response.status_code}")
            return None, None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None, None

def main():
    if not os.path.exists(URLS_FILE):
        print(f"File {URLS_FILE} not found.")
        return

    with open(URLS_FILE, 'r') as f:
        urls = [line.strip() for line in f if line.strip().startswith('http')]

    print(f"Found {len(urls)} URLs.")

    success_count = 0
    limit = 20 # Process 20 per run

    for i, url in enumerate(urls):
        arxiv_id = url.split('/')[-1]
        filename = f"{arxiv_id}.md"
        filepath = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(filepath):
            print(f"Skipping {url}: File exists")
            continue

        title, abstract = fetch_article(url)

        if title and abstract:
            content = f"""# {title}

Link: {url}

## Abstract
{abstract}

## Relevance to CodeSwarm
TODO: Analyze relevance.

## Key Offerings
TODO: Extract useful ideas.
"""
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            success_count += 1
            print(f"Saved {filename}")

            time.sleep(1)

        if success_count >= limit:
            print(f"Batch limit reached ({limit} papers).")
            break

if __name__ == "__main__":
    main()
