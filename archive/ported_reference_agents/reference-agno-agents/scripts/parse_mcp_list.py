import re
import json
import argparse
from pathlib import Path

def parse_mcp_line(line: str):
    # Regex for: 134. **\[mcp\]**: Description. [url](url)
    # Pattern: Number. **\[(Name)\]**: (Description) [(Url)](Url)
    # Note: The brackets around Name might be escaped as \[ \] or just [ ] depending on MD flavor. User showed \[mcp\].

    # Try pattern with escaped brackets
    pattern = r"^\d+\.\s+\*\*\\\[(.*?)\\\]\*\*:\s+(.*?)\s+\[(.*?)\]\((.*?)\)"
    match = re.search(pattern, line)

    if not match:
        # Try unescaped
        pattern = r"^\d+\.\s+\*\*\[(.*?)\]\*\*:\s+(.*?)\s+\[(.*?)\]\((.*?)\)"
        match = re.search(pattern, line)

    # Fallback: Maybe no brackets in name?
    # 134. **mcp**: ...
    if not match:
        pattern = r"^\d+\.\s+\*\*(.*?)\*\*:\s+(.*?)\s+\[(.*?)\]\((.*?)\)"
        match = re.search(pattern, line)

    if match:
        return {
            "name": match.group(1),
            "description": match.group(2).strip(),
            "url": match.group(4),
            "source": "community_list"
        }
    return None

def parse_file(input_path: str, output_path: str):
    entries = []
    seen_urls = set()
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                entry = parse_mcp_line(line)
                if entry:
                    if entry["url"] not in seen_urls:
                        entries.append(entry)
                        seen_urls.add(entry["url"])
                else:
                    print(f"Skipped line: {line[:50]}...")
    except FileNotFoundError:
        print(f"File not found: {input_path}")
        return

    # Load existing if exists to append? Or overwrite? Overwrite for now.
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    print(f"Parsed {len(entries)} items to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input MD file")
    parser.add_argument("output", help="Output JSON file")
    args = parser.parse_args()

    parse_file(args.input, args.output)
