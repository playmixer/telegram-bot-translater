import json
import os
from datetime import datetime
import urllib.parse
import urllib.request

from io import BytesIO

from core.configurations import TMP_FOLDER
from core.logger import logger


class Requests:
    _html = b''
    _response = None
    _file = None
    tmp_folder = None
    files = []

    def __init__(self, tmp):
        self.tmp_folder = tmp

    def get(self, url):
        with urllib.request.urlopen(url) as response:
            self._html = response.read()
            self._response = response
        return self

    def post(self, url, headers: dict = {}, data: dict = {}):
        try:
            log = 'post ' + url
            data = json.dumps(data)
            req = urllib.request.Request(url)
            for key in headers.keys():
                req.add_header(key, headers[key])
            log += req.headers
            log += req.data
            response = urllib.request.urlopen(req, data.encode('utf-8'))
            log += response.read()
            self._html = response.read()
            self._response = response
        except Exception as err:
            logger.error(str(err))

        logger.debug(log)
        return self

    def get_f(self, url, headers: dict = {}):
        req = urllib.request.Request(url)
        for key in headers.keys():
            req.add_header(key, headers[key])
        response = urllib.request.urlopen(req)
        self._response = response
        self._file = response.read()
        return self

    def get_f2(self, url, headers: dict = {}):
        req = urllib.request.build_opener()
        for key in headers.keys():
            req.addheaders.append((key, headers[key]))

        urllib.request.install_opener(req)
        filename = os.path.join(TMP_FOLDER, f'file_{datetime.now().strftime("%Y%m%d%H%M%S%f")}')
        urllib.request.urlretrieve(url, filename)
        self._file = filename
        return self

    def get_f3(self, url, headers: dict = {}):
        req = urllib.request.Request(url)
        for key in headers.keys():
            req.add_header(key, headers[key])
        response = urllib.request.urlopen(req)

        buffer = BytesIO()
        while True:
            chunk = response.read()
            if not chunk:
                break
            buffer.write(chunk)
        self._file = buffer

        self._response = response
        return self

    def status(self):
        return self._response.status()

    def text(self):
        return self._html

    def file(self):
        return self._file

    def json(self):
        try:
            return json.loads(self._html)
        except json.decoder.JSONDecodeError as err:
            print(str(err))
            return None


request = Requests(tmp=TMP_FOLDER)
