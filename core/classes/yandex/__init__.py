import json
import requests
import os

from core.configurations import YANDEX_TOKEN, YANDEX_FOLDER, TMP_FOLDER
from core.classes.data import Data
from datetime import datetime, timedelta
from core.logger import logger
from core.classes.user import User
from core.utils import save_to_tmp


def _date_format(d):
    return datetime.strptime(d[:19], '%Y-%m-%dT%H:%M:%S')


TTS_LANG_RU = 'ru-RU'
TTS_LANG_EN = 'en-US'
TTS_LANG_TR = 'tr-TR'

T_LANG_EN = 'en'
T_LANG_RU = 'ru'
T_LANG_TR = 'tr'

EMOTION_GOOD = 'good'
EMOTION_EVIL = 'evil'
EMOTION_NEUTRAL = 'neutral'

VOICE_OKSANA = 'oksana'
VOICE_JANE = 'jane'
VOICE_OMAZH = 'omazh'
VOICE_ZAHAR = 'zahar'
VOICE_ERMIL = 'ermil'

LANG_DICT = {
    'ru': (T_LANG_RU, TTS_LANG_RU),
    'en': (T_LANG_EN, TTS_LANG_EN),
    'tr': (T_LANG_TR, TTS_LANG_TR)
}


class YandexException(Exception):
    ...


class Yandex:
    user: User = None
    token: str = None
    folderId: str = None
    iam: str = None
    expire_iam: datetime = None
    response: dict = {}
    text: str = None
    detected_language: str = None
    file = None
    _speed: str = '0.9'
    _emotion: str = EMOTION_GOOD
    _voice: str = VOICE_OMAZH
    _tts_lang: str = TTS_LANG_EN
    _translate_lang: str = T_LANG_EN

    def __init__(self):
        self.token = YANDEX_TOKEN
        self.folderId = YANDEX_FOLDER
        self.update_configurations()

        if self.iam is None or self.expire_iam is None or datetime.utcnow() - timedelta(hours=2) > self.expire_iam:
            yandex = self.get_iam_token()
            if yandex is not None:
                self.iam = yandex.get('iamToken')
                self.expire_iam = _date_format(yandex.get('expiresAt'))
                with Data() as d:
                    d.set('yandex', yandex)

    def set_user(self, user: User):
        self.user = user

    def update_configurations(self):
        with Data() as d:
            yandex = d.get('yandex')
            if yandex and yandex.get('iamToken') and yandex.get('expiresAt'):
                self.iam = yandex.get('iamToken')
                self.expire_iam = _date_format(yandex.get('expiresAt'))
                self._speed = d.get('speed') or self._speed
                self._emotion = d.get('emotion') or self._emotion
                self._voice = d.get('voice') or self._voice
                lang = d.get('lang')
                lang_dict = LANG_DICT[lang if lang is not None else 'en']
                if lang and lang_dict:
                    self._translate_lang, self._tts_lang = lang_dict
                else:
                    self._tts_lang = d.get('tts_lang') or self._tts_lang
                    self._translate_lang = d.get('translate_lang') or self._translate_lang

    def get_iam_token(self):
        log = 'Yandex.get_iam_token'
        url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
        data = {"yandexPassportOauthToken": self.token}
        log += '\n\tRequest: '
        log += '\n\tdata: ' + json.dumps(data)
        res = requests.post(
            url,
            # headers=headers,
            json=data
        )
        if res.status_code == 200:
            data = res.json()
            log += '\n\tResponse: ' + json.dumps(data)
            logger.debug(log)
            return data

        log += '\n\tResponse: ' + res.text
        logger.debug(log)
        return None

    def translate(self, text: str, settings: User = None):
        url = 'https://translate.api.cloud.yandex.net/translate/v2/translate'
        log = f'Yandex.translate'

        target = None
        lang = LANG_DICT.get(settings.target_lang)
        if lang is not None:
            target, _ = lang

        headers = {"Authorization": f"Bearer {self.iam}"}
        data = {
            "folderId": self.folderId,
            "texts": [text],
            "targetLanguageCode": self._translate_lang if target is None else target
        }
        log += '\n\theaders: ' + json.dumps(headers)
        log += '\n\tdata: ' + json.dumps(data)
        res = requests.post(url, headers=headers, json=data)

        if res.status_code == 200:
            self.response = res.json()
            log += '\n\tResponse text : ' + json.dumps(res.json())

            translations = self.response.get('translations')
            if translations:
                self.text = translations[0].get('text')
                self.detected_language = translations[0].get('detectedLanguageCode')
            else:
                self.text = "ERROR"

        logger.debug(log)
        return self

    def tts(self, text: str, settings: User = None):
        url = f"https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
        log = "Yandex.tts"

        target = None
        lang = LANG_DICT.get(settings.target_lang)
        if lang is not None:
            _, target = lang

        data = {
            'folderId': self.folderId,
            'text': text,
            'lang': self._tts_lang if target is None else target,
            'speed': settings.speed if settings.speed else self._speed,
            'emotion': settings.emotion if settings.emotion else self._emotion,
            'voice': settings.voice if settings.voice else self._voice
        }
        log += "\n\tQuery: " + json.dumps(data)
        r = requests.post(url, headers={"Authorization": f"Bearer {self.iam}"}, data=data)
        filename = os.path.join(TMP_FOLDER, f'file_{datetime.now().strftime("%Y%m%d%H%M%S%f")}.ogg')
        if r.status_code == 200:
            save_to_tmp(r.content, prefix='file_', end='.ogg')
            log += "\n\tResponse completed"
            # with open(filename, 'wb') as f:
            #     f.write(r.content)
        else:
            log += "\n\tError: " + r.text

        logger.debug(log)
        self.file = filename
        return self

    def recognize(self, filename: str):
        url = f'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize'
        headers = {
            "Authorization": f"Bearer {self.iam}",
        }
        data = {
            "folderId": self.folderId,
            "lang": "ru-RU",
        }
        log = f'''Yandex.recognize url {url}\n\theaders: {json.dumps(headers)}\n\tdata: {json.dumps(data)}'''
        with open(filename, 'rb') as f:
            file = f.read()
        r = requests.post(url, headers=headers, params=data, data=file)
        logger.debug(log + f"\n\tResponse: {r.text}")
        if r.status_code == 200:
            result = r.json().get('result')
            return result
        return None
