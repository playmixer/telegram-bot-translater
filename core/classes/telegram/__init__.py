from typing import List
from core.request import request
import urllib
import urllib.parse
import requests
from core.logger import logger
from core.configurations import TG_BOT_TOKEN


class TGExceptionErrorToken(Exception):
    ...


class TelegramMessage:
    update_id: str = None
    message_id: str = None
    text: str = None
    voice: dict = None
    from_id: str = None
    chat_id: str = None

    def __init__(self, json: dict):
        self.update_id = json.get('update_id')
        _from = json.get('from')
        if _from:
            self.from_id = _from.get('id')

        message = json.get('message')
        if message:
            self.message_id = message.get('message_id')
            self.text = message.get('text')
            self.voice = message.get('voice')
            chat = message.get('chat')
            if chat:
                self.chat_id = chat.get('id')


class TelegramResult:
    ok: bool = None
    messages: List[TelegramMessage] = []

    def __init__(self, json: dict):
        self.ok = json.get('ok')
        if self.ok:
            messages = json.get('result')
            self.messages = []
            for message in messages:
                self.messages.append(TelegramMessage(message))


class Telegram:
    _api = f'https://api.telegram.org/bot'
    _file = f'https://api.telegram.org/file/bot'
    first_name = None
    username = None

    def __init__(self, token):
        self._api = f'https://api.telegram.org/bot{token}/'
        self._file = f'https://api.telegram.org/file/bot{token}/'

    @staticmethod
    def create():
        bot = Telegram(TG_BOT_TOKEN)
        return bot

    def get_me(self):
        url = self._api + 'getMe'

        res = request.get(url)
        json = res.json()
        if json.get('ok'):
            result = json.get('result')
            if result:
                self.first_name = result.get('first_name')
                self.username = result.get('username')

        return json

    def get_update(self, offset: int = None):
        import json
        url = self._api + 'getUpdates'
        if offset:
            url += '?offset=' + str(offset)
        log = f'Telegram.get_update {url}'
        r_json = request.get(url).json()
        if r_json.get('result') and len(r_json.get('result')):
            log += f"\n\tResponse: {json.dumps(r_json)}"
        logger.debug(log)
        return TelegramResult(r_json)

    def send_message(self, chat_id: int, text: str = ""):
        data = {
            "chat_id": chat_id,
            "text": text
        }
        url = self._api + f'sendMessage'
        logger.debug('Telegram.send_message url: \n\t' + url + "\n\t" + str(data))
        json = requests.post(url, data=data).json()
        logger.debug(json)
        return json

    def send_voice(self, chat_id=None, voice=None, caption=None):
        url = self._api + f'sendVoice'
        res = requests.post(url, data={'chat_id': chat_id, 'caption': caption}, files={'voice': voice})
        json = res.json()
        logger.debug(f'''Telegram.send_voice\n\tResponse: {res.text}''')
        return json

    def get_file(self, file_id: str):
        url = self._api + 'getFile'
        data = {
            "file_id": file_id
        }
        import json
        log = f'''Telegram.get_file url: {url}\n\t{json.dumps(data)}'''
        res = requests.get(url, data=data)
        res_json = res.json()
        log += "\n\tResponse text: " + res.text
        result = res_json.get('result')
        if res_json.get('ok') and result:
            file_path = result.get('file_path')
            if file_path:
                url_file = self._file + file_path
                res = requests.get(url_file)
                if res.status_code == 200:
                    logger.debug(log + "\n\tDownload completed")
                    return res.content
        logger.debug(log + "\n\tDownload failed")
        return None
