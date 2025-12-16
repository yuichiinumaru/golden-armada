import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_backlog.py <file_with_urls>")
        sys.exit(1)

    input_file = sys.argv[1]

    with open(input_file, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]

    print("# Research Backlog\n")
    print("Master tracking file for Arxiv paper analysis.\n")

    for line in lines:
        clean_line = line
        if clean_line.endswith('.pdf'):
            clean_line = clean_line[:-4]

        if "arxiv.org" in clean_line:
            parts = clean_line.split('/')
            paper_id = parts[-1]
        else:
            paper_id = clean_line

        # Basic validation
        if not paper_id:
            continue

        print(f"### [ ] Paper {paper_id}")
        print(f"- **Status:** Pending")
        print(f"- **Artifact:** `docs/ideas/{paper_id}.md`")
        print("- **Tasks:**")
        print(f"  - [ ] Agent: Read `docs/arxiv/{paper_id}.pdf` fully.")
        print("  - [ ] Agent: Deeply analyze current codebase architecture to understand context.")
        print("  - [ ] Agent: Brainstorm integration points (Paper Idea -> Codebase Module).")
        print("  - [ ] Agent: Perform Gap Analysis (What exists vs What is needed).")
        print(f"  - [ ] Agent: Write `docs/ideas/{paper_id}.md` using the Standard Template.")
        print("")

if __name__ == "__main__":
    main()
