import argparse
import asyncio
import time

from data_loader import run_mllp_client
import data_processing
from pager import *
import model_feature_construction
import pandas as pd
import pickle
import threading


def main(history_data, mllp, pager, sex_encoder, aki_encoder, clf_model):
    http_pager = Pager()
    asyncio.run(run_http_pager(pager))
    shutdown_mllp = threading.Event()
    t = threading.Thread(target=run_mllp_client, args=("0.0.0.0", mllp, shutdown_mllp, sex_encoder,
                                                       aki_encoder, clf_model, pager, history_data), daemon=True)
    t.start()
    time.sleep(10)
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Detected CTRL+C, safely exiting.")
        # Perform cleanup here
        asyncio.run(close_http_pager(pager))
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

    main(df, flags.mllp, flags.pager, sex_encoder, aki_encoder, clf_model)
