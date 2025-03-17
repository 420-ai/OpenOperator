from typing import Dict, List, Any
from pydantic import BaseModel

class ProxyConfig(BaseModel):
    host: str = '0.0.0.0'
    port: int = 8080

class ProxyResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any] = {}

class UrlsResponse(BaseModel):
    urls: List[str]
