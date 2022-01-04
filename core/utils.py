import os
from datetime import datetime
from typing import Tuple

from core.configurations import TMP_FOLDER
from core.logger import logger


def mk_path(path: list):
    for i in range(1, len(path) + 1):
        p = os.path.join(*path[:i])
        if not os.path.exists(p):
            os.mkdir(p)


def command_split(text: str) -> Tuple[str, str]:
    s = text.split(' ')
    return s[0][1:], s[1] if len(s) > 1 else None


def save_to_tmp(file, prefix='file_', end='') -> str:
    filename = os.path.join(TMP_FOLDER, f'{prefix}{datetime.now().strftime("%Y%m%d%H%M%S%f")}{end}')
    with open(filename, 'wb') as f:
        f.write(file)
        logger.debug(f'save_to_tmp file: {filename}')
        return filename
