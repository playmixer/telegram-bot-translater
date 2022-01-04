import os
from dotenv import load_dotenv

load_dotenv()

TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')

YANDEX_TOKEN = os.getenv('YANDEX_TOKEN')
YANDEX_FOLDER = os.getenv('YANDEX_FOLDER')

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

TMP_FOLDER = os.path.join(BASE_PATH, '..', 'tmp')
