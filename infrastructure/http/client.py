import httpx
from typing import Any

from infrastructure.logger import get_logger

app_logger = get_logger("http")

from .models import HTTPClientMode, ResponseType

class HTTPClient:
	_client: httpx.Client | None = None
	_async_client: httpx.AsyncClient | None = None

	def __init__(self, mode: HTTPClientMode = HTTPClientMode.sync, headers: dict | None = None, autoconnect: bool = False):
		if not isinstance(mode, HTTPClientMode):
			try:
				mode = HTTPClientMode(mode)
			except ValueError:
				raise ValueError(f"Invalid mode {mode}, must be 'sync' or 'async'")
		self.mode = mode
		self.headers = headers or {}
		self.timeout = httpx.Timeout(
			connect=10.0,	# таймаут на установку соединения
			read=60.0,		# ожидание ответа сервера
			write=60.0,		# отправка данных (важно для файлов)
			pool=60.0		# операции с пулом соединений
		)
		if autoconnect:
			self.get_client() if self.mode == HTTPClientMode.sync else self.get_async_client()

	# ----------------- Сессии -----------------
	def get_client(self) -> httpx.Client:
		if self._client is None:
			self._client = httpx.Client(timeout=self.timeout)
			app_logger.info("🌐 Client [httpx] connected")
		return self._client

	def get_async_client(self) -> httpx.AsyncClient:
		if self._async_client is None:
			self._async_client = httpx.AsyncClient(timeout=self.timeout)
			app_logger.info("🌐 Async Client [httpx] connected")
		return self._async_client

	# ----------------- Закрытие -----------------
	def close(self):
		if self._client:
			self._client.close()
			self._client = None
			app_logger.info("🌐 Client [httpx] disconnected")

	async def close_async(self):
		if self._async_client:
			await self._async_client.aclose()
			self._async_client = None
			app_logger.info("🌐 Async Client [httpx] disconnected")

	# ----------------- HEADERS -----------------
	def _get_headers(self, data: dict | None):
		headers = self.headers.copy()
		if data:
			headers.update(data)
		return headers

	# ----------------- GET -----------------
	def get(self, url: str, response_type: ResponseType = ResponseType.json, raise_for_status: bool = False, **kwargs):
		if self.mode == HTTPClientMode.async_:
			raise RuntimeError("Use 'aget' for async mode")
		kwargs["headers"] = self._get_headers(kwargs.get("headers"))
		resp = self.get_client().get(url, **kwargs)
		return self._handle_response(response=resp, response_type=response_type, raise_for_status=raise_for_status)

	async def aget(self, url: str, response_type: ResponseType = ResponseType.json, raise_for_status: bool = False, **kwargs):
		if self.mode == HTTPClientMode.sync:
			raise RuntimeError("Use 'get' for sync mode")
		client = self.get_async_client()
		kwargs["headers"] = self._get_headers(kwargs.get("headers"))
		resp = await client.get(url, **kwargs)
		return self._handle_response(response=resp, response_type=response_type, raise_for_status=raise_for_status)

	# ----------------- POST -----------------
	def post(self, url: str, response_type: ResponseType = ResponseType.json, raise_for_status: bool = False, **kwargs):
		if self.mode == HTTPClientMode.async_:
			raise RuntimeError("Use 'apost' for async mode")
		kwargs["headers"] = self._get_headers(kwargs.get("headers"))
		resp = self.get_client().post(url, **kwargs)
		return self._handle_response(response=resp, response_type=response_type, raise_for_status=raise_for_status)

	async def apost(self, url: str, response_type: ResponseType = ResponseType.json, raise_for_status: bool = False, **kwargs):
		if self.mode == HTTPClientMode.sync:
			raise RuntimeError("Use 'post' for sync mode")
		client = self.get_async_client()
		kwargs["headers"] = self._get_headers(kwargs.get("headers"))
		resp = await client.post(url, **kwargs)
		return self._handle_response(response=resp, response_type=response_type, raise_for_status=raise_for_status)

	# ----------------- PUT -----------------
	def put(self, url: str, response_type: ResponseType = ResponseType.json, raise_for_status: bool = False, **kwargs):
		if self.mode == HTTPClientMode.async_:
			raise RuntimeError("Use 'aput' for async mode")
		kwargs["headers"] = self._get_headers(kwargs.get("headers"))
		resp = self.get_client().put(url, **kwargs)
		return self._handle_response(response=resp, response_type=response_type, raise_for_status=raise_for_status)

	async def aput(self, url: str, response_type: ResponseType = ResponseType.json, raise_for_status: bool = False, **kwargs):
		if self.mode == HTTPClientMode.sync:
			raise RuntimeError("Use 'put' for sync mode")
		client = self.get_async_client()
		kwargs["headers"] = self._get_headers(kwargs.get("headers"))
		resp = await client.put(url, **kwargs)
		return self._handle_response(response=resp, response_type=response_type, raise_for_status=raise_for_status)

	# ----------------- PATCH -----------------
	def patch(self, url: str, response_type: ResponseType = ResponseType.json, raise_for_status: bool = False, **kwargs):
		if self.mode == HTTPClientMode.async_:
			raise RuntimeError("Use 'apatch' for async mode")
		kwargs["headers"] = self._get_headers(kwargs.get("headers"))
		resp = self.get_client().patch(url, **kwargs)
		return self._handle_response(response=resp, response_type=response_type, raise_for_status=raise_for_status)

	async def apatch(self, url: str, response_type: ResponseType = ResponseType.json, raise_for_status: bool = False, **kwargs):
		if self.mode == HTTPClientMode.sync:
			raise RuntimeError("Use 'patch' for sync mode")
		client = self.get_async_client()
		kwargs["headers"] = self._get_headers(kwargs.get("headers"))
		resp = await client.patch(url, **kwargs)
		return self._handle_response(response=resp, response_type=response_type, raise_for_status=raise_for_status)

	# ----------------- RESPONSE -----------------
	def _handle_response(self, response: httpx.Response, response_type: ResponseType, raise_for_status: bool) -> Any:
		if raise_for_status:
			response.raise_for_status()

		match response_type:
			case ResponseType.response:
				return response
			case ResponseType.json:
				try:
					return response.json()
				except ValueError:
					app_logger.warning("Response is not valid JSON, returning text instead")
					return response.text
			case ResponseType.text:
				return response.text
			case ResponseType.raw:
				return response.content

	def __getattr__(self, name):
		def sync_wrapper(*args, **kwargs):
			client = self.get_client()
			method = getattr(client, name)
			return method(*args, **kwargs)

		async def async_wrapper(*args, **kwargs):
			client = self.get_async_client()
			method = getattr(client, name)
			return await method(*args, **kwargs)

		if self.mode == HTTPClientMode.sync:
			return sync_wrapper
		else:
			return async_wrapper
