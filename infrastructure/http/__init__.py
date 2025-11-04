from .client import HTTPClient
from .models import HTTPClientMode

sync_http_client = HTTPClient(mode="sync")
async_http_client = HTTPClient(mode="async")
