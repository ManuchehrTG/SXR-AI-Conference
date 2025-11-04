from functools import wraps
from time import time
from typing import Any, Callable, TypeVar, cast
import logging

F = TypeVar('F', bound=Callable[..., Any])

def get_logger(name: str) -> logging.Logger:
	"""Получить логгер по имени"""
	return logging.getLogger(name)

def log_execution_time(logger: logging.Logger | None = None):
	"""Декоратор для логирования времени выполнения функции"""
	def decorator(func: F) -> F:
		@wraps(func)
		async def async_wrapper(*args, **kwargs):
			start_time = time()
			try:
				result = await func(*args, **kwargs)
				return result
			finally:
				execution_time = time() - start_time
				log = logger or get_logger(func.__module__)
				log.debug(f"⏱️ {func.__name__} executed in {execution_time:.4f}s")

		@wraps(func)
		def sync_wrapper(*args, **kwargs):
			start_time = time()
			try:
				result = func(*args, **kwargs)
				return result
			finally:
				execution_time = time() - start_time
				log = logger or get_logger(func.__module__)
				log.debug(f"⏱️ {func.__name__} executed in {execution_time:.4f}s")
		
		if func.__code__.co_flags & 0x80:  # Check if function is async
			return cast(F, async_wrapper)
		else:
			return cast(F, sync_wrapper)

	return decorator

class LoggerMixin:
	"""Миксин/Descriptor для добавления логгера в классы"""
	def __get__(self, instance, owner):
		class_obj = owner if instance is None else instance.__class__
		if not hasattr(class_obj, '_logger'):
			class_name = class_obj.__name__
			class_obj._logger = get_logger(f"{class_obj.__module__}.{class_name}")
		return class_obj._logger

	@property
	def logger(self) -> logging.Logger:
		"""Логгер с именем класса"""
		if not hasattr(self, '_logger'):
			class_name = self.__class__.__name__
			self._logger = get_logger(f"{self.__module__}.{class_name}")
		return self._logger
