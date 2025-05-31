import os
from typing import List
from bs4 import BeautifulSoup
import requests
import subprocess

def create_file(file_path: str, content: str) -> dict:
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {'status': 'success', 'result': f"File '{file_path}' created successfully."}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def read_file(file_path: str) -> dict:
    resolved_file_path = file_path
    target_base = os.environ.get("TARGET_PROJECT_PATH_FOR_TOOLS")
    try:
        if os.path.isabs(file_path):
            if target_base and not file_path.startswith(target_base):
                file_basename = os.path.basename(file_path)
                resolved_file_path = os.path.normpath(os.path.join(target_base, file_basename))
                print(f"DEBUG: read_file: Absolute path '{file_path}' was outside TARGET_PROJECT_PATH_FOR_TOOLS. Resolved to '{resolved_file_path}'.")
            else:
                resolved_file_path = os.path.normpath(file_path)
                print(f"DEBUG: read_file: Absolute path '{file_path}' used as is or already within target_base.")
        else: # It's a relative path
            if target_base:
                target_base_name = os.path.basename(target_base)
                if file_path.startswith(target_base_name + os.path.sep):
                    file_path_corrected = file_path[len(target_base_name) + len(os.path.sep):]
                    print(f"DEBUG: read_file: Corrected relative path from '{file_path}' to '{file_path_corrected}'.")
                    file_path = file_path_corrected
                resolved_file_path = os.path.normpath(os.path.join(target_base, file_path))
                print(f"DEBUG: read_file: Relative path '{file_path}' (post-correction) resolved to '{resolved_file_path}' using TARGET_PROJECT_PATH_FOR_TOOLS.")
            else:
                resolved_file_path = os.path.normpath(file_path)
                print(f"DEBUG: read_file: Relative path '{file_path}' received, but TARGET_PROJECT_PATH_FOR_TOOLS not set. Using as is.")

        print(f"Attempting to read file at final path: {resolved_file_path}")
        with open(resolved_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"Successfully read file: {resolved_file_path}")
        return {'status': 'success', 'content': content}
    except Exception as e:
        print(f"Error in read_file for original path '{file_path}' (final resolved path '{resolved_file_path}'): {e}")
        return {'status': 'error', 'message': str(e)}

def update_file(file_path: str, new_content: str) -> dict:
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return {'status': 'success', 'result': f"File '{file_path}' updated successfully."}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def delete_file(file_path: str) -> dict:
    try:
        os.remove(file_path)
        return {'status': 'success', 'result': f"File '{file_path}' deleted successfully."}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def execute_python_code(code: str) -> dict:
    try:
        result = subprocess.run(['python', '-c', code], capture_output=True, text=True, timeout=10)
        return {'status': 'success', 'stdout': result.stdout, 'stderr': result.stderr}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def execute_shell_command(command: str) -> dict:
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        return {'status': 'success', 'stdout': result.stdout, 'stderr': result.stderr}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def write_file(file_path: str, content: str) -> dict:
    """Writes the given content to the specified file, overwriting if it exists.
    Args:
        file_path (str): The absolute or relative path to the file to be written.
        content (str): The content to write to the file.
    Returns:
        dict: {'status': 'success', 'result': str} on success, or {'status': 'error', 'message': str} on failure.
    """
    resolved_file_path = file_path
    target_base = os.environ.get("TARGET_PROJECT_PATH_FOR_TOOLS")

    try:
        if os.path.isabs(file_path):
            if target_base and not file_path.startswith(target_base):
                # LLM provided an absolute path that is NOT within the target project base.
                # Force it into the target_base using only the basename of the LLM's path.
                file_basename = os.path.basename(file_path)
                resolved_file_path = os.path.normpath(os.path.join(target_base, file_basename))
                print(f"DEBUG: write_file: Absolute path '{file_path}' was outside TARGET_PROJECT_PATH_FOR_TOOLS. Resolved to '{resolved_file_path}'.")
            else:
                # Absolute path is already within target_base or target_base is not set (less safe, but keep original if it's all we have)
                resolved_file_path = os.path.normpath(file_path)
                print(f"DEBUG: write_file: Absolute path '{file_path}' used as is or already within target_base.")
        else: # It's a relative path
            if target_base:
                # Path correction: if file_path (e.g., "project_dir/file.txt") redundantly starts with
                # the basename of target_base (e.g., "/abs/path/to/project_dir"), strip it.
                target_base_name = os.path.basename(target_base)
                if file_path.startswith(target_base_name + os.path.sep):
                    file_path_corrected = file_path[len(target_base_name) + len(os.path.sep):]
                    print(f"DEBUG: write_file: Corrected relative path from '{file_path}' to '{file_path_corrected}'.")
                    file_path = file_path_corrected # Use the corrected path for joining

                resolved_file_path = os.path.normpath(os.path.join(target_base, file_path))
                print(f"DEBUG: write_file: Relative path '{file_path}' (post-correction) resolved to '{resolved_file_path}' using TARGET_PROJECT_PATH_FOR_TOOLS.")
            else:
                # Relative path and no target_base, use as is (relative to CWD)
                resolved_file_path = os.path.normpath(file_path)
                print(f"DEBUG: write_file: Relative path '{file_path}' received, but TARGET_PROJECT_PATH_FOR_TOOLS not set. Using as is (relative to CWD).")

        print(f"Attempting to write file at final path: {resolved_file_path}")
        dir_name = os.path.dirname(resolved_file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        with open(resolved_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully wrote file: {resolved_file_path}")
        return {"status": "success", "result": f"Wrote file: {resolved_file_path}"}
    except Exception as e:
        print(f"Error in write_file for original path '{file_path}' (final resolved path '{resolved_file_path}'): {e}")
        return {"status": "error", "message": str(e)}

def list_folder_contents(folder_path: str) -> dict:
    """Lists the files and folders in the specified directory.
    Args:
        folder_path (str): The path to the directory to list.
    Returns:
        dict: {'status': 'success', 'content': List[str]} on success, or {'status': 'error', 'message': str} on failure.
    """
    try:
        items = os.listdir(folder_path)
        return {"status": "success", "content": items}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def search_files_content(folder_path: str, search_query: str) -> dict:
    """Searches for a string in all files under the given folder (recursively).
    Args:
        folder_path (str): The root folder to search.
        search_query (str): The string to search for.
    Returns:
        dict: {'status': 'success', 'content': List[str]} (list of file paths containing the query), or {'status': 'error', 'message': str}.
    """
    if not os.path.isdir(folder_path):
        return {"status": "error", "message": f"Directory not found: {folder_path}"}

    matches = []
    try:
        for root, _, files in os.walk(folder_path):
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        if search_query in f.read():
                            matches.append(fpath)
                except Exception:
                    continue
        return {"status": "success", "content": matches}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def fetch_web_page_text_content(url: str) -> dict:
    """Fetches and returns the visible text content of a web page.
    Args:
        url (str): The URL to fetch.
    Returns:
        dict: {'status': 'success', 'content': str} on success, or {'status': 'error', 'message': str} on failure.
    """
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return {"status": "success", "content": text}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def chunk_file(file_path: str, max_chunk_size: int = 4000) -> dict:
    """Reads a file and splits its content into chunks of up to max_chunk_size characters.
    Args:
        file_path (str): Path to the file.
        max_chunk_size (int): Maximum size of each chunk (in characters).
    Returns:
        dict: {'status': 'success', 'content': List[str]} on success, or {'status': 'error', 'message': str}.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        chunks = [content[i:i+max_chunk_size] for i in range(0, len(content), max_chunk_size)]
        return {"status": "success", "content": chunks}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def summarize_chunks(chunks: List[str], summarizer_fn) -> dict:
    """Sequentially summarizes a list of text chunks using the provided summarizer function.
    Args:
        chunks (List[str]): List of text chunks.
        summarizer_fn (callable): Function that takes a string and returns a summary string.
    Returns:
        dict: {'status': 'success', 'content': str} (combined summary), or {'status': 'error', 'message': str}.
    """
    try:
        summaries = [summarizer_fn(chunk) for chunk in chunks]
        combined = "\n".join(summaries)
        return {"status": "success", "content": combined}
    except Exception as e:
        return {"status": "error", "message": str(e)} 