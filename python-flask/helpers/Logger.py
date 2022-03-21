import logging

import structlog

structlog.configure(processors=[
    structlog.stdlib.filter_by_level,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.TimeStamper(fmt="iso", utc=True),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.UnicodeDecoder(),
    structlog.processors.JSONRenderer()
],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logging.basicConfig(level=logging.INFO)
logging = structlog.get_logger("flask")


def bind_logging(request):
    request_headers_without_sensitive_data = delete_cookie_key_from(dict(request.headers))
    return logging.bind(
        addr=request.remote_addr,
        url=request.url,
        method=request.method,
        headers=request_headers_without_sensitive_data,
        params=request.args
    )


def delete_cookie_key_from(request_headers):
    try:
        del request_headers["Cookie"]
    except KeyError:
        pass

    return request_headers
