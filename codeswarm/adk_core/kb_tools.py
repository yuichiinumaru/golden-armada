# codeswarm/adk_core/kb_tools.py
import os
from typing import List, Dict, Union

DOCS_ROOT_PATH = "./docs" # Relative to the project root (where main_adk_controller is run from)

def list_docs_in_kb() -> List[str]:
    """Lists all available documents in the project's /docs knowledge base."""
    try:
        all_files_and_dirs = []
        # Ensure DOCS_ROOT_PATH exists
        if not os.path.isdir(DOCS_ROOT_PATH):
            return [f"Error: DOCS_ROOT_PATH '{DOCS_ROOT_PATH}' does not exist or is not a directory."]

        for root, dirs, files in os.walk(DOCS_ROOT_PATH):
            for name in files:
                # Construct relative path from DOCS_ROOT_PATH
                relative_path = os.path.relpath(os.path.join(root, name), DOCS_ROOT_PATH)
                all_files_and_dirs.append(relative_path)
            for name in dirs:
                relative_path = os.path.relpath(os.path.join(root, name), DOCS_ROOT_PATH)
                all_files_and_dirs.append(relative_path + os.path.sep) # Add trailing slash for directories
        return sorted(all_files_and_dirs)
    except Exception as e:
        return [f"Error listing documents: {str(e)}"]

def get_doc_content_from_kb(filepath_relative_to_docs: str) -> str:
    """
    Reads and returns the content of a specified document from the /docs folder.
    Provide the filepath relative to the /docs folder (e.g., 'project.md' or 'adkdocs/adk-imports.md').
    """
    if not filepath_relative_to_docs or ".." in filepath_relative_to_docs or filepath_relative_to_docs.startswith("/"):
        return "Error: Invalid filepath provided. Must be relative to /docs and not contain '..'."
    try:
        actual_filepath = os.path.join(DOCS_ROOT_PATH, filepath_relative_to_docs)

        if not os.path.exists(actual_filepath) or not os.path.isfile(actual_filepath):
            return f"Error: Document '{filepath_relative_to_docs}' not found in '{DOCS_ROOT_PATH}' (resolved to '{actual_filepath}')."
        with open(actual_filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading document '{filepath_relative_to_docs}': {str(e)}"

def search_docs_in_kb(query: str, filepath_relative_to_docs: str = None) -> Union[List[Dict[str, str]], str]:
    """
    Searches for a query within documents in the /docs folder.
    If a filepath_relative_to_docs is provided, searches only within that file.
    Returns a list of dictionaries, each containing 'filepath' and 'snippet' of relevant content.
    """
    if not query:
        return "Error: Query cannot be empty."

    results = []
    files_to_search = []

    if not os.path.isdir(DOCS_ROOT_PATH):
        return f"Error: DOCS_ROOT_PATH '{DOCS_ROOT_PATH}' does not exist or is not a directory."

    if filepath_relative_to_docs:
        if ".." in filepath_relative_to_docs or filepath_relative_to_docs.startswith("/"):
             return "Error: Invalid filepath for search."
        full_path_to_check = os.path.join(DOCS_ROOT_PATH, filepath_relative_to_docs)
        if os.path.exists(full_path_to_check) and os.path.isfile(full_path_to_check):
            files_to_search.append(filepath_relative_to_docs)
        else:
            return f"Error: Specified document '{filepath_relative_to_docs}' not found in '{DOCS_ROOT_PATH}' for searching (resolved to '{full_path_to_check}')."
    else:
        all_docs_listing = list_docs_in_kb()
        if isinstance(all_docs_listing, list) and all_docs_listing and "Error:" in all_docs_listing[0] and all_docs_listing[0].startswith("Error:"):
             return f"Error accessing /docs for search: {all_docs_listing[0]}"
        files_to_search = [f for f in all_docs_listing if not f.endswith(os.path.sep)]


    for doc_path in files_to_search:
        content = get_doc_content_from_kb(doc_path)
        if content.startswith("Error:"): # Check if it's an actual error message
            print(f"Warning: Could not read file {doc_path} for searching: {content}")
            continue

        lines = content.splitlines()
        for i, line in enumerate(lines):
            if query.lower() in line.lower(): # Simple case-insensitive search
                snippet_start = max(0, i - 1) # one line before
                snippet_end = min(len(lines), i + 2) # matched line and one line after
                snippet = "\n".join(lines[snippet_start:snippet_end])
                results.append({"filepath": doc_path, "snippet": snippet, "matched_line": i + 1})
                if len(results) >= 5: # Limit to 5 results for brevity
                    break
        if len(results) >= 5:
            break

    if not results:
        return f"No relevant content found for '{query}' in the searched documents."
    return results
```
