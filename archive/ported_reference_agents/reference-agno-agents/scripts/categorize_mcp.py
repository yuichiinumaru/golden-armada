import json
import os
import re
import requests
import concurrent.futures
from pathlib import Path
from collections import defaultdict
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

REGISTRY_PATH = Path("services/agent_os/app/lib/mcp_registry.json")
OUTPUT_DIR = Path("docs/mcplist")
OUTPUT_JSON_PATH = REGISTRY_PATH  # Overwrite

CATEGORIES = {
    "01-security": ["pentest", "scan", "nmap", "kali", "burp", "exploit", "cve", "vulnerability", "wireshark", "shodan", "osint", "security", "hack", "attack", "defense", "metasploit", "bloodhound"],
    "02-database": ["sql", "postgres", "mysql", "redis", "vector", "pinecone", "mongodb", "sqlite", "db", "database", "storage", "s3", "minio", "elasticsearch", "search", "chroma", "qdrant", "milvus", "weaviate", "clickhouse", "snowflake", "bigquery"],
    "03-cloud-infra": ["aws", "google cloud", "azure", "kubernetes", "docker", "terraform", "server", "linux", "windows", "mac", "shell", "cli", "infrastructure", "monitor", "log", "observability", "prometheus", "grafana", "home assistant", "iot", "ssh"],
    "04-development": ["git", "github", "gitlab", "ide", "vscode", "python", "javascript", "typescript", "java", "rust", "go", "code", "debug", "compiler", "build", "ci/cd", "api", "sdk", "package", "registry", "jetbrains", "xcode", "npm", "pip"],
    "05-productivity": ["notion", "linear", "jira", "slack", "discord", "email", "calendar", "todo", "task", "note", "obsidian", "google workspace", "office", "zoom", "teams", "asana", "trello", "airtable"],
    "06-web-browser": ["browser", "scrape", "crawl", "search", "google search", "bing", "duckduckgo", "fetch", "download", "content", "web", "html", "http"],
    "07-ai-llm": ["openai", "anthropic", "gemini", "llama", "model", "memory", "rag", "embedding", "chat", "assistant", "agent", "prompt", "llm", "gpt", "claude"],
    "08-finance-crypto": ["crypto", "bitcoin", "ethereum", "solana", "finance", "stock", "market", "payment", "bank", "trading", "price", "currency", "wallet"],
    "09-media-content": ["image", "video", "audio", "text", "pdf", "markdown", "youtube", "spotify", "social", "instagram", "tiktok", "facebook", "twitter", "media", "art", "music"],
    "10-uncategorized": []
}

CATEGORY_TITLES = {
    "01-security": "Security & OSINT",
    "02-database": "Databases & Storage",
    "03-cloud-infra": "Cloud & Infrastructure",
    "04-development": "Development Tools",
    "05-productivity": "Productivity & Collaboration",
    "06-web-browser": "Web & Browser",
    "07-ai-llm": "AI & LLM",
    "08-finance-crypto": "Finance & Crypto",
    "09-media-content": "Media & Content",
    "10-uncategorized": "Uncategorized"
}

def get_readme_url(github_url):
    """Converts a GitHub repo URL to a raw README URL."""
    # https://github.com/user/repo -> https://raw.githubusercontent.com/user/repo/HEAD/README.md
    match = re.match(r"https?://github\.com/([^/]+)/([^/]+)", github_url)
    if match:
        user, repo = match.groups()
        repo = repo.replace(".git", "")
        return f"https://raw.githubusercontent.com/{user}/{repo}/HEAD/README.md"
    return None

def fetch_readme_description(url, current_desc):
    """
    Fetches the README and extracts a better description if possible.
    Returns (success, new_description, categories_found)
    """
    readme_url = get_readme_url(url)
    if not readme_url:
        return False, current_desc, []

    try:
        response = requests.get(readme_url, timeout=5)
        if response.status_code == 200:
            content = response.text
            # Simple heuristic: Look for the first paragraph after the header
            # Or just return the content to analyze keywords

            # Analyze keywords in README for better categorization
            content_lower = content.lower()
            return True, current_desc, content_lower # Return content for categorization
        else:
            # Try master branch if HEAD fails (sometimes HEAD isn't supported by raw?)
            # Actually HEAD usually works. Maybe 'main' or 'master' explicitly.
            pass
    except Exception as e:
        logger.warning(f"Failed to fetch {readme_url}: {e}")

    return False, current_desc, ""

def categorize_item(item, readme_content=""):
    """
    Categorizes an item based on name, description, and optional README content.
    """
    text = (item["name"] + " " + item["description"] + " " + readme_content).lower()

    # Check strict matches first
    for cat, keywords in CATEGORIES.items():
        if cat == "10-uncategorized": continue
        for kw in keywords:
            # Word boundary check for better accuracy
            if re.search(r'\b' + re.escape(kw) + r'\b', text):
                return cat

    return "10-uncategorized"

def process_item(item):
    """
    Process a single item: fetch info, categorize.
    """
    # Create a copy
    new_item = item.copy()

    # Fetch README (optional verification)
    # Note: We don't want to overwrite the description automatically unless we are sure.
    # But we use the content for categorization.
    success, _, readme_content = fetch_readme_description(new_item["url"], new_item["description"])

    category = categorize_item(new_item, readme_content if success else "")
    new_item["category"] = category

    if success:
        new_item["verified"] = True
    else:
        new_item["verified"] = False

    return new_item

def main():
    if not REGISTRY_PATH.exists():
        print(f"Registry not found at {REGISTRY_PATH}")
        return

    with open(REGISTRY_PATH, "r") as f:
        registry = json.load(f)

    print(f"Loaded {len(registry)} items.")

    enhanced_registry = []

    # Use ThreadPool for concurrency
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_item, item): item for item in registry}

        count = 0
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                enhanced_registry.append(result)
                count += 1
                if count % 50 == 0:
                    print(f"Processed {count}/{len(registry)}")
            except Exception as e:
                logger.error(f"Error processing item: {e}")

    # Sort registry
    enhanced_registry.sort(key=lambda x: x["name"].lower())

    # Save Enhanced JSON
    with open(OUTPUT_JSON_PATH, "w") as f:
        json.dump(enhanced_registry, f, indent=2, ensure_ascii=False)
    print(f"Saved enhanced registry to {OUTPUT_JSON_PATH}")

    # Generate MD Files
    by_category = defaultdict(list)
    for item in enhanced_registry:
        by_category[item["category"]].append(item)

    # Ensure output dir exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    index_content = "# MCP Server Index\n\n"
    index_content += "This index lists Model Context Protocol (MCP) servers categorized by functionality.\n\n"

    for cat_key in sorted(CATEGORIES.keys()):
        items = by_category[cat_key]
        if not items:
            continue

        title = CATEGORY_TITLES[cat_key]
        filename = f"{cat_key}.md"
        file_path = OUTPUT_DIR / filename

        index_content += f"- [{title}](./{filename}) ({len(items)})\n"

        md_content = f"# {title}\n\n"
        md_content += f"Found {len(items)} MCP servers in this category.\n\n"

        # Sort items alphabetically
        items.sort(key=lambda x: x["name"].lower())

        for item in items:
            status = "✅" if item.get("verified") else "⚠️"
            md_content += f"### {item['name']} {status}\n"
            md_content += f"**Description**: {item['description']}\n\n"
            md_content += f"**URL**: [{item['url']}]({item['url']})\n\n"
            md_content += "---\n\n"

        with open(file_path, "w") as f:
            f.write(md_content)
        print(f"Generated {filename}")

    # Write Index
    with open(OUTPUT_DIR / "00-index.md", "w") as f:
        f.write(index_content)
    print("Generated 00-index.md")

if __name__ == "__main__":
    main()
