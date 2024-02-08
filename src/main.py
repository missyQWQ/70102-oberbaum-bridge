#!/usr/bin/env python3
import argparse
from data_loader import run_mllp_client
from pager import *
import pandas as pd
import pickle
import multiprocessing
import warnings


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


if __name__ == "__main__":
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
