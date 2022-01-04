from time import sleep
import os
import asyncio

from .logger import logger
from core import configurations
from .classes import yandex
from core.classes.data import Data
from core.classes.telegram import Telegram, TelegramMessage, TelegramResult
from core.classes.user import User
from core.utils import command_split, save_to_tmp
from .core import Command

bot = Telegram.create()


class VoicerConfig:
    tts_enable = True

    def __init__(self, config_dict: dict):
        if config_dict is not None:
            tts_enable = config_dict.get('tts') if config_dict.get('tts') is not None else True
            self.tts_enable = tts_enable


class VoiceApplication:
    tts_enable = True
    config: VoicerConfig = None

    def __init__(self, config_dict=None):
        self.config = VoicerConfig(config_dict)

    def command_processing(self, message: TelegramMessage):
        with Data() as d:
            command, value = command_split(message.text)
            cmd = Command()
            try:
                if cmd.list().index(command) >= 0:
                    cmd.get(command)
                    d.set(command, cmd.type(value) if value else cmd.default)
            except ValueError:
                pass

    async def handler(self, message: TelegramMessage):
        '''
        Обработчик входящего сообщения
        :param message:
        :return:
        '''
        # Обрабатываем текстовое сообщение
        try:
            user = User(message.chat_id)
            ya_app = yandex.Yandex()

            # Команда
            if message.text and message.text.startswith('/'):
                if user.user_id:
                    command, value = user.command_processing(message)
                    bot.send_message(message.chat_id, f'Параметр {command} изменен на {value}')
                else:
                    self.command_processing(message)

            # Переводим текст
            else:
                # Проверяем кол-во доступных попыток
                if not user.attempts_per_day:
                    bot.send_message(message.chat_id, 'Лимит исчерпан')
                else:
                    if message.text:
                        ya_app.translate(message.text, settings=user)
                        # Возвращаем голосовое сообщение
                        # если разрешено
                        if self.config.tts_enable and user.tts:
                            voice = ya_app.tts(ya_app.text, settings=user).file
                            if os.path.exists(voice):
                                with open(voice, 'rb') as f:
                                    data_file = f.read()
                                bot.send_voice(message.chat_id, voice=data_file, caption=ya_app.text)
                                os.remove(voice)
                        # текстовое сообщение
                        else:
                            bot.send_message(message.chat_id, ya_app.text)
                        # Уменьшаем остаток проб перевода
                        user.attempt_decrement()

                    # Обрабатываем голосовое сообщение
                    if message.voice:
                        file_id = message.voice.get('file_id')
                        file = bot.get_file(file_id)
                        if file:
                            filename = save_to_tmp(file, 'voice_', end='.ogg')
                            # распознаем
                            if filename:
                                text = ya_app.recognize(filename)
                                # if os.path.exists(filename):
                                os.remove(filename)
                                # перевод
                                ya_app.translate(text, settings=user)
                                if self.config.tts_enable and user.tts:
                                    voice = ya_app.tts(ya_app.text, settings=user).file
                                    # if os.path.exists(voice):
                                    with open(voice, 'rb') as f:
                                        data_file = f.read()
                                    bot.send_voice(message.chat_id, voice=data_file, caption=text + "\n" + ya_app.text)
                                    user.attempt_decrement()
                                    os.remove(voice)
                                # текстовое сообщение
                                else:
                                    bot.send_message(message.chat_id, ya_app.text)
                                # Уменьшаем остаток проб перевода
                                user.attempt_decrement()

                        else:
                            bot.send_message(message.chat_id, 'Ошибка загрузки ауди сообщения')

        except Exception as err:
            logger.error('Voicer.handler error ' + str(err))

    async def run(self):
        with Data() as d:
            update_id = d.get('update_id') or 1

        # save_id = update_id
        while True:
            result: TelegramResult = bot.get_update(update_id + 1)

            # Обрабатываем все сообщения
            handlers = [self.handler(message) for message in result.messages]
            await asyncio.gather(*handlers)

            # Сохраняем номер последнего сообщения
            last_message: list[TelegramMessage] = result.messages[-1:]
            if len(last_message):
                update_id = last_message[0].update_id
                with Data() as d:
                    d.set('update_id', last_message[0].update_id)

            await asyncio.sleep(1)

    def start(self):
        try:
            print("Запускаем программу")
            logger.debug("Start app")
            asyncio.run(self.run())
        except KeyboardInterrupt:
            print("Завершаем программу")
            logger.debug("Stop app")
        # except Exception as err:
        #     print(str(err))
        #     logger.debug(str(err))
