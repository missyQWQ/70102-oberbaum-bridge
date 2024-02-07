#!/usr/bin/env python3
import argparse
import asyncio
import time

from data_loader import run_mllp_client
import data_processing
from pager import *
import model_feature_construction
import pandas as pd
import pickle
import multiprocessing


def main(history_data, mllp, pager, sex_encoder, aki_encoder, clf_model):
    http_pager = Pager("http://localhost:8441/page")
    shutdown_mllp = multiprocessing.Event()
    t = multiprocessing.Process(target=run_mllp_client, args=("0.0.0.0", mllp, shutdown_mllp, sex_encoder,
                                                    aki_encoder, clf_model, pager, http_pager, history_data), daemon=True)
    t.start()
    print("Server started...")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Detected CTRL+C, safely exiting.")
        # Perform cleanup here
        shutdown_mllp.set()
    t.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", default="history.csv", help="History Creatine Record to be used for predictions")
    parser.add_argument("--mllp", default=8440, type=int,
                        help="Port connecting server to receives HL7 messages via MLLP")
    parser.add_argument("--pager", default=8441, type=int, help="Post on which to listen for pager requests via HTTP")
    parser.add_argument("--sex_encoder", default='sex_encoder_model.pkl',
                        help="Post on which to listen for pager requests via HTTP")
    parser.add_argument("--aki_encoder", default='aki_encoder_model.pkl',
                        help="Post on which to listen for pager requests via HTTP")
    parser.add_argument("--clf_model", default='clf_model.pkl',
                        help="Post on which to listen for pager requests via HTTP")
    parser.add_argument("--http", default='http://localhost:8441/page', help="URL to send page requests to pager system")

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
    main(df, flags.mllp, flags.pager, sex_encoder, aki_encoder, clf_model)
