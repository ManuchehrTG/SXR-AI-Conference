import logging.config

# Конфигурация для logging.config.dictConfig
LOGGING_CONFIG = {
	"version": 1,
	"disable_existing_loggers": False,
	"formatters": {
		"standard": {
			"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
			"datefmt": "%Y-%m-%d %H:%M:%S",
		},
		"detailed": {
			"format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
			"datefmt": "%Y-%m-%d %H:%M:%S",
		},
	},
	"handlers": {
		"console": {
			"class": "logging.StreamHandler",
			"level": "INFO",
			"formatter": "standard",
			"stream": "ext://sys.stdout",
		},
		"file": {
			"class": "logging.handlers.RotatingFileHandler",
			"level": "DEBUG",
			"formatter": "detailed",
			"filename": "logs/app.log",
			"maxBytes": 10 * 1024 * 1024,  # 10 MB
			"backupCount": 5,
			"encoding": "utf8",
		},
	},
	"loggers": {
		"": {  # Root logger
			"handlers": ["console", "file"],
			"level": "INFO",
			"propagate": False
		},
		"app": {
			"handlers": ["console", "file"],
			"level": "DEBUG",
			"propagate": False,
		},
		"infrastructure": {
			"handlers": ["console", "file"],
			"level": "INFO",
			"propagate": False,
		},
		"telegram_bot": {
			"handlers": ["console", "file"],
			"level": "INFO",
			"propagate": False,
		},
		"backend": {
			"handlers": ["console", "file"],
			"level": "INFO",
			"propagate": False,
		},
	},
}