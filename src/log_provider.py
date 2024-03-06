import logging
import os

# CLASS LOG_PROVIDER
# The class provides logger for all modules.

# Check if log file exists
if not os.path.exists("/state"):
    os.makedirs("/state")
    open("/state/app.log", 'x')


# Config log file.
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    filename='/state/app.log',
                    filemode='a')


# Log API wrapper
def get_logger(name):
    return logging.getLogger(name)
