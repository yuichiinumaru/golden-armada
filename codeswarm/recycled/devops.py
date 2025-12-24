"""Recycled DevOps and utility logic."""

import os
import subprocess
import json
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

def docker_pull(image_name: str) -> Dict[str, Any]:
    """Pulls a Docker image."""
    try:
        result = subprocess.run(['docker', 'pull', image_name], capture_output=True, text=True, check=True)
        return {'status': 'success', 'result': result.stdout}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def docker_build(path: str, tag: str) -> Dict[str, Any]:
    """Builds a Docker image."""
    try:
        result = subprocess.run(['docker', 'build', '-t', tag, path], capture_output=True, text=True, check=True)
        return {'status': 'success', 'result': result.stdout}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def read_config(path: str) -> Dict[str, Any]:
    """Reads a JSON configuration file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return {'status': 'success', 'config': json.load(f)}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def fetch_web_text(url: str) -> Dict[str, Any]:
    """Fetches text content from a URL."""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        return {'status': 'success', 'content': soup.get_text(separator=' ', strip=True)}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def chunk_text(text: str, max_size: int = 4000) -> List[str]:
    """Splits text into chunks."""
    return [text[i:i+max_size] for i in range(0, len(text), max_size)]
