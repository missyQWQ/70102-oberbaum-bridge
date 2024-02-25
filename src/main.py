#!/usr/bin/env python3
import argparse
import os

from data_loader import run_mllp_client
from pager import *
import pandas as pd
import pickle
import multiprocessing
import warnings
from data_provider import DataProvider
import signal
import sys
import time
import os
from run_model import EnsembleModel
from prometheus_client import start_http_server
from log_provider import get_logger

state_data = None


def main(mllp, pager, aki_model):
    warnings.filterwarnings('ignore', category=FutureWarning)
    warnings.filterwarnings('ignore', category=RuntimeWarning)
    http_pager = Pager(f"http://{pager}/page")

    ip_address, port_str = mllp.split(":")
    # Convert port string to integer
    port_number = int(port_str)
    print('Promethus Client Starts')
    start_http_server(8000)
    print("Server started...")
    run_mllp_client(ip_address, port_number, aki_model, http_pager, state_data)


def save_variables(filename):
    with open(filename, 'wb') as file:
        pickle.dump(state_data, file)


# Reload requested data variable to file
"""def load_variables(filename):
    with open(filename, 'rb') as file:
        return pickle.load(file)"""


def signal_handler(sig, frame):
    get_logger(__name__).critical(f'{sig} received, dump state')
    print(f'{sig} received, graceful shutdown!!!!!!!!!!!')
    save_variables('/state/state.pkl')
    sys.exit(0)


"""def load_state():
    global data_provider
    data_provider = load_variables('/state/state.pkl')
    print(f"Data loaded!!!!!!!")"""

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument("--history", default="history.csv", help="History Creatine Record to be used for predictions")
    parser.add_argument("--MLLP_ADDRESS", default='0.0.0.0:8440',
                        help="Port connecting server to receives HL7 messages via MLLP")
    parser.add_argument("--PAGER_ADDRESS", default='0.0.0.0:8441',
                        help="Post on which to listen for pager requests via HTTP")
    parser.add_argument("--sex_encoder", default='sex_encoder_model.pkl',
                        help="Post on which to listen for pager requests via HTTP")
    parser.add_argument("--aki_encoder", default='aki_encoder_model.pkl',
                        help="Post on which to listen for pager requests via HTTP")
    parser.add_argument("--clf_model", default='clf_model.pkl',
                        help="Post on which to listen for pager requests via HTTP")
    parser.add_argument("--http", default='http://localhost:8441/page',
                        help="URL to send page requests to pager system")

    flags = parser.parse_args()

    if os.path.exists('/state/state.pkl'):
        get_logger(__name__).critical('Try to recover from previous state!!!')
        print("Loading state....")
        with open('/state/state.pkl', 'rb') as file:
            state_data = pickle.load(file)
    else:
        print("Loading data....")
        state_data = DataProvider()
        history_data_df = pd.read_csv(flags.history)
        state_data.set_history(history_data_df)
        get_logger(__name__).info('Data loaded')

    sex_encoder = None
    aki_encoder = None
    clf_model = None
    with open(flags.sex_encoder, "rb") as file:
        sex_encoder = pickle.load(file)
    with open(flags.aki_encoder, "rb") as file:
        aki_encoder = pickle.load(file)
    with open(flags.clf_model, "rb") as file:
        clf_model = pickle.load(file)
    print("Cached, Ready to run server")
    aki_model = EnsembleModel(sex_encoder, aki_encoder, clf_model)
    get_logger(__name__).info("Cached, Ready to run server")
    main(flags.MLLP_ADDRESS, flags.PAGER_ADDRESS, aki_model)
