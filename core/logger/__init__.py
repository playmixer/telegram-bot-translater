import logging
from logging import handlers
import os

directory = 'logs'
filename = os.path.join(directory, 'app.log')

if not os.path.exists(directory):
    os.mkdir(directory)

# if not os.path.exists(filename):
#     with open(filename, 'w') as f:
#         ...

format_logs = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename=filename, level=logging.DEBUG, format=format_logs)

logger = logging.getLogger('voicer')
logger.setLevel(logging.DEBUG)

hand = handlers.TimedRotatingFileHandler(filename, when="midnight", interval=1)
hand.suffix = "%Y%m%d"
logger.addHandler(hand)
