import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    filename='state/app.log',
                    filemode='a')


def get_logger(name):
    return logging.getLogger(name)
