from lib.config import Config

def validate_api_key(api_key: str) -> bool:
    if not Config.API_KEYS or not api_key:
        return False
    return api_key in Config.API_KEYS
