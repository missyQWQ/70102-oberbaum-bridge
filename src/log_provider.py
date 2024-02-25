import logging
import os

if not os.path.exists("/state"):
    os.makedirs("/state")
    open("/state/app.log", 'x')


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    filename='/state/app.log',
                    filemode='a')


def get_logger(name):
    return logging.getLogger(name)
