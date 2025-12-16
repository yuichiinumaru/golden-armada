import os
import sys
import time
import requests

def download_file(url, filepath):
    headers = {
        'User-Agent': 'CodeSwarm-ResearchAgent/1.0 (mailto:admin@codeswarm.local)'
    }
    try:
        response = requests.get(url, stream=True, timeout=30, headers=headers)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded: {filepath}")
            return True
        else:
            print(f"Failed to download {url}: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_papers.py <file_with_urls>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = os.path.join(os.getcwd(), "docs/arxiv")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]

    print(f"Found {len(lines)} papers to process.")

    for line in lines:
        # Extract ID.
        # Example: https://arxiv.org/pdf/1501.01613
        # or https://arxiv.org/pdf/1501.01613.pdf (sometimes user might provide with pdf extension)

        clean_line = line
        if clean_line.endswith('.pdf'):
            clean_line = clean_line[:-4]

        if "arxiv.org" in clean_line:
            parts = clean_line.split('/')
            paper_id = parts[-1]
        else:
            paper_id = clean_line

        # Verify if paper_id is empty or weird
        if not paper_id:
            print(f"Skipping invalid line: {line}")
            continue

        url = f"https://arxiv.org/pdf/{paper_id}.pdf"
        filepath = os.path.join(output_dir, f"{paper_id}.pdf")

        if os.path.exists(filepath):
            print(f"Skipping {paper_id}, already exists.")
            continue

        print(f"Processing {paper_id}...")
        success = download_file(url, filepath)
        if success:
            time.sleep(1) # Be polite to Arxiv

if __name__ == "__main__":
    main()
