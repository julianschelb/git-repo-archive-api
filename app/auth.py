from fastapi.security.api_key import APIKeyHeader
from fastapi import Security, HTTPException
from starlette.status import HTTP_403_FORBIDDEN
import json


def read_api_keys(file_path):
    """Read API Keys from JSON file"""
    with open(file_path, 'r') as file:
        data = json.load(file)

    api_keys = [item['key'] for item in data]
    return api_keys


# API Key Header
api_key_header = APIKeyHeader(name="access_token", auto_error=False)

# Read API Keys
api_keys = read_api_keys('api_keys.json')


async def get_api_key(api_key_header: str = Security(api_key_header)):
    """API Key Validation"""
    if api_key_header in api_keys:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )
