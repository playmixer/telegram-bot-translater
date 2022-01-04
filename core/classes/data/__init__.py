import os
import json

from core.utils import mk_path


class Data:
    data = None
    _filename = None

    def __init__(self, filename='data.json'):
        split_path: list = filename.split(os.sep)[:-1]
        mk_path(split_path)
        self._filename = filename
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                json.dump({}, f)
                self.data = {}

    # def open(self):
    #     with open(self._filename, 'r') as f:
    #         text = f.read()
    #         self.data = json.loads(text)
    #     return self
    #
    # def save(self, data):
    #     with open(self._filename, 'w') as f:
    #         json.dump(self.data, f)

    def __enter__(self):
        with open(self._filename, 'r') as f:
            text = f.read()
            self.data = json.loads(text)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open(self._filename, 'w') as f:
            json.dump(self.data, f)

    def set(self, variable=None, value=None):
        if variable is not None and value is not None:
            self.data[variable] = value

    def get(self, variable=None):
        if variable:
            return self.data.get(variable)
