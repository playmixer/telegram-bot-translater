import os
import json

from core.classes.data import Data
from core.classes.telegram import TelegramMessage
from core.core import Command
from core.utils import command_split


class UserDataNotHaveUserId(Exception):
    ...


class UserData(Data):
    def __init__(self, user_id: str):
        if user_id:
            filename = os.path.join('data', 'users', f'{user_id}.data')
            super().__init__(filename)
            with open(self._filename, 'r') as f:
                self.data = json.loads(f.read())
        else:
            raise UserDataNotHaveUserId


class User:
    user_id: str = None
    voice: str = None
    speed: str = '1.0'
    target_lang: str = 'en'
    emotion: str = 'goo'
    tts: int = 1

    data = {}

    def __init__(self, user_id: str):
        from core.classes import yandex
        self.user_id = user_id
        with UserData(user_id) as d:
            self.data = d.data
            self.voice = d.get('voice') or yandex.VOICE_ZAHAR
            self.speed = d.get('speed') or '1.0'
            self.target_lang = d.get('lang') or 'en'
            self.tts = int(d.get('tts')) if d.get('tts') is not None else 1
            self.emotion = d.get('emotion') or 'good'

    def __call__(self, *args, **kwargs):
        return self.user_id

    def command_processing(self, message: TelegramMessage):
        with UserData(self.user_id) as d:
            command, value = command_split(message.text)
            cmd = Command()
            try:
                if cmd.list().index(command) >= 0:
                    cmd.get(command)
                    d.set(command, cmd.type(value) if value else cmd.default)
            except ValueError:
                pass
