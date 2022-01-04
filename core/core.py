class Command:
    _commands = {
        'voice': [str, ''],
        'speed': [float, 0.9],
        'emotion': [str, ''],
        'lang': [str, 'ru'],
        'tts': [int, 1]
    }

    def get(self, command: str):
        self.command = command
        self.type, self.default = self._commands[command][0], self._commands[command][1]

    def list(self) -> list:
        return [v for v in self._commands.keys()]
