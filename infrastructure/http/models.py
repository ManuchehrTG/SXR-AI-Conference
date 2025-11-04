from enum import Enum

class HTTPClientMode(str, Enum):
	sync = "sync"
	async_ = "async"

class ResponseType(str, Enum):
	response = "response"
	json = "json"
	text = "text"
	raw = "raw"
