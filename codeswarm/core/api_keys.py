import os
import requests
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

def get_api_key_from_rotation_service(service_url: str) -> Optional[str]:
    """Get API key from rotation service."""
    try:
        response = requests.get(f"{service_url}/api-key", timeout=5)
        response.raise_for_status()
        data = response.json()
        logger.info(f"🔑 Retrieved API key from rotation service (index: {data.get('key_index', 'unknown')})")
        return data["api_key"]
    except Exception as e:
        logger.warning(f"⚠️ Failed to get API key from rotation service: {e}")
        return None

def get_api_key_local() -> str:
    """Get API key using local rotation from environment variables."""
    keys_str = os.environ.get("GENAI_API_KEYS")
    if keys_str:
        keys = [key.strip() for key in keys_str.split(',')]
        if keys:
            # Simple round-robin implementation based on time
            index = int(time.time()) % len(keys)
            logger.info(f"🔑 Using local API key rotation (index: {index})")
            return keys[index]

    # Fallback to single key
    single_key = os.environ.get("GOOGLE_API_KEY")
    if single_key:
        logger.info("🔑 Using single API key")
        return single_key

    raise ValueError("No API keys found in environment variables. Please set GENAI_API_KEYS or GOOGLE_API_KEY.")

def get_api_key() -> str:
    """Get API key using the best available method."""
    use_rotation_service = os.environ.get("USE_ROTATION_SERVICE", "false").lower() == "true"
    service_url = os.environ.get("API_KEY_ROTATION_SERVICE_URL")

    if use_rotation_service and service_url:
        key = get_api_key_from_rotation_service(service_url)
        if key:
            return key

    return get_api_key_local()
