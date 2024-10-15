import base64
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def encode_id(id: str) -> str:
    try:
        return base64.urlsafe_b64encode(str(id).encode()).decode()
    except Exception as e:
        logger.error(f"Failed to encode ID: {id}. Error: {type(e).__name__} - {e}")
        return None


def decode_id(id: str) -> str:
    try:
        return str(base64.urlsafe_b64decode(id).decode())
    except Exception as e:
        logger.error(f"Unexpected error decoding ID: {id}. Error: {type(e).__name__} - {e}")
        return None
