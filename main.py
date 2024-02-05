import argparse
import data_loader
import data_processing
import pager
import model_feature_construction

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--messages", default="messages.mllp", help="HL7 messages to replay, in MLLP format")
    parser.add_argument("--history", default="history.csv", help="History Creatine Record to be used for predictions")
    parser.add_argument("--mllp", default=8440, type=int, help="Port on which to replay HL7 messages via MLLP")
    parser.add_argument("--pager", default=8441, type=int, help="Post on which to listen for pager requests via HTTP")
    flags = parser.parse_args()

    history_data_df = pd.read_csv(history_data_path)
    df = history_data_df.copy()
    main()