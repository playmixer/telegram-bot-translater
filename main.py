from core import Voicer, Data

with Data() as d:
    data = d.data

app = Voicer(config_dict=data)

app.run()
