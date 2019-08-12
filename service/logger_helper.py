import logging
from functools import wraps
from flask import request


def log_request(request_func):
    """
    Simple request logging decorator
    :param request_func: request to be processed
    :return: Response object
    """

    @wraps(request_func)
    def logging_decorator(*args, **kwargs):
        logging.info(f"{request.method} request to endpoint {request_func.__name__} for {request.path}")
        return request_func(*args, **kwargs)

    return logging_decorator