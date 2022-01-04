from core import VoiceApplication, Data

with Data() as d:
    data = d.data

app = VoiceApplication(config_dict=data)

app.start()
