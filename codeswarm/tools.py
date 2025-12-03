import os
import subprocess
import requests
from bs4 import BeautifulSoup
from typing import List
from . import config

def _is_safe_path(file_path: str) -> bool:
    """Validates that the file path is within the allowed project directory."""
    try:
        target_path = os.path.abspath(config.DEFAULT_PROJECT_PATH)
        requested_path = os.path.abspath(file_path)
        return os.path.commonpath([target_path, requested_path]) == target_path
    except Exception:
        return False

def create_file(file_path: str, content: str) -> dict:
    """Creates a file with the given content.

    Args:
        file_path (str): The absolute path to the file to be created.
        content (str): The content to write to the file.

    Returns:
        dict: {'status': 'success', 'result': str} or {'status': 'error', 'message': str}
    """
    if not _is_safe_path(file_path):
        return {'status': 'error', 'message': f"Access denied: {file_path} is outside the project directory."}
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {'status': 'success', 'result': f"File '{file_path}' created successfully."}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def read_file(file_path: str) -> dict:
    """Reads and returns the entire content of the specified file.

    Args:
        file_path (str): The absolute path to the file to be read.

    Returns:
        dict: {'status': 'success', 'content': str} or {'status': 'error', 'message': str}
    """
    if not _is_safe_path(file_path):
        return {'status': 'error', 'message': f"Access denied: {file_path} is outside the project directory."}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {'status': 'success', 'content': content}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def update_file(file_path: str, new_content: str) -> dict:
    """Updates a file with new content.

    Args:
        file_path (str): The absolute path to the file to be updated.
        new_content (str): The new content for the file.

    Returns:
        dict: {'status': 'success', 'result': str} or {'status': 'error', 'message': str}
    """
    if not _is_safe_path(file_path):
        return {'status': 'error', 'message': f"Access denied: {file_path} is outside the project directory."}
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return {'status': 'success', 'result': f"File '{file_path}' updated successfully."}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def delete_file(file_path: str) -> dict:
    """Deletes the specified file.

    Args:
        file_path (str): The absolute path to the file to delete.

    Returns:
        dict: {'status': 'success', 'result': str} or {'status': 'error', 'message': str}
    """
    if not _is_safe_path(file_path):
        return {'status': 'error', 'message': f"Access denied: {file_path} is outside the project directory."}
    try:
        os.remove(file_path)
        return {'status': 'success', 'result': f"File '{file_path}' deleted successfully."}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def execute_python_code(code: str) -> dict:
    """Executes Python code.

    Args:
        code (str): The Python code to execute.

    Returns:
        dict: {'status': 'success', 'stdout': str, 'stderr': str} or {'status': 'error', 'message': str}
    """
    try:
        result = subprocess.run(['python', '-c', code], capture_output=True, text=True, timeout=10)
        return {'status': 'success', 'stdout': result.stdout, 'stderr': result.stderr}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def execute_shell_command(command: str) -> dict:
    """Executes a shell command.

    Args:
        command (str): The shell command to execute.

    Returns:
        dict: {'status': 'success', 'stdout': str, 'stderr': str} or {'status': 'error', 'message': str}
    """
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        return {'status': 'success', 'stdout': result.stdout, 'stderr': result.stderr}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def write_file(file_path: str, content: str) -> dict:
    """Writes the given content to the specified file, overwriting if it exists.

    Args:
        file_path (str): The absolute path to the file to be written.
        content (str): The content to write to the file.

    Returns:
        dict: {'status': 'success', 'result': str} on success, or {'status': 'error', 'message': str} on failure.
    """
    if not _is_safe_path(file_path):
        return {'status': 'error', 'message': f"Access denied: {file_path} is outside the project directory."}
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "success", "result": f"Wrote file: {file_path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def list_folder_contents(folder_path: str) -> dict:
    """Lists the files and folders in the specified directory.

    Args:
        folder_path (str): The path to the directory to list.

    Returns:
        dict: {'status': 'success', 'content': List[str]} on success, or {'status': 'error', 'message': str} on failure.
    """
    if not _is_safe_path(folder_path):
        return {'status': 'error', 'message': f"Access denied: {folder_path} is outside the project directory."}
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
    if not _is_safe_path(folder_path):
        return {'status': 'error', 'message': f"Access denied: {folder_path} is outside the project directory."}
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
    if not _is_safe_path(file_path):
        return {'status': 'error', 'message': f"Access denied: {file_path} is outside the project directory."}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        chunks = [content[i:i+max_chunk_size] for i in range(0, len(content), max_chunk_size)]
        return {"status": "success", "content": chunks}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def summarize_chunks(chunks: List[str]) -> dict:
    """
    Provides chunks of text that an agent can then use to make summarization calls to an LLM.

    Args:
        chunks (List[str]): List of text chunks to be prepared for summarization.

    Returns:
        dict: {'status': 'success', 'prepared_chunks': list[str]}
    """
    if not isinstance(chunks, list):
          return {"status": "error", "message": "Input 'chunks' must be a list."}
    return {"status": "success", "prepared_chunks": chunks}
