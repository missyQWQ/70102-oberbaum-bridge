#!/usr/bin/env python3
import argparse
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

data_provider = DataProvider()


def main(history_data, mllp, pager, sex_encoder, aki_encoder, clf_model):
    warnings.filterwarnings('ignore', category=FutureWarning)
    http_pager = Pager(f"http://{pager}/page")
    shutdown_mllp = multiprocessing.Event()
    ip_address, port_str = mllp.split(":")
    # Convert port string to integer
    port_number = int(port_str)
    print("Server started...")
    run_mllp_client(ip_address, port_number, shutdown_mllp, sex_encoder, aki_encoder, clf_model, pager, http_pager,
                    history_data)


def save_variables(filename, variables):
    with open(filename, 'wb') as file:
        pickle.dump(variables, file)


# Reload requested data variable to file
def load_variables(filename):
    with open(filename, 'rb') as file:
        return pickle.load(file)


def signal_handler(sig, frame):
    print(f'{sig} received, graceful shutdown!!!!!!!!!!!')
    state = data_provider
    save_variables('/state/state.pkl', state)
    sys.exit(0)


def load_state():
    global data_provider
    data_provider = load_variables('/state/state.pkl')
    print(f"Data loaded!!!!!!!")


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
    history_data_df = pd.read_csv(flags.history)
    df = history_data_df.copy()
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
    main(df, flags.MLLP_ADDRESS, flags.PAGER_ADDRESS, sex_encoder, aki_encoder, clf_model)

print('Application is running...')
while True:
    # 模拟应用程序长时间运行
    time.sleep(1)
