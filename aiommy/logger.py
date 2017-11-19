import datetime
import json
import logging


class Logger(object):
    def __init__(self, name, path, level):
        self._logger = logging.getLogger(name)

        file_handler_path = path
        file_handler = logging.FileHandler(file_handler_path)

        self._logger.addHandler(file_handler)

        self._logger.setLevel(level)

    @property
    def logger(self):
        return self._logger

    def error(self, msg):
        self.logger.error(msg)


class LoggerHTTPResponse(Logger):
    def http_error(self, request, response):
        user = 'Anonymous'
        if hasattr(request, 'user') and request.user is not None:
            user = request.user.get('id')

        msg = """
status: {status}
    timestamp: {timestamp}
    method: {method}
    path: {path}
    headers: {headers}
    user: {user}
    text: {text}
        """.format(status=response.status,
                   timestamp=str(datetime.datetime.utcnow()),
                   method=request.method,
                   path=request.path,
                   headers=json.dumps(dict(request.headers)),
                   user=user,
                   text=response.text)
        self.logger.error(msg)


class ApiDeprecatedLogger(Logger):
    def deprecated_error(self, msg):
        self.logger.error("""
error: {error}
    timestamp: {timestamp}
        """.format(error=msg, timestamp=str(datetime.datetime.utcnow())))
