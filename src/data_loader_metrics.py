import socket
import time
from datetime import datetime
from pager import *
from data_processing import data_combination_dfAndDict
from model_feature_construction import preprocess_features
from run_model import Model
import numpy as np
import math

VERSION = "0.0.0"
MLLP_BUFFER_SIZE = 1024
MLLP_TIMEOUT_SECONDS = 10
SHUTDOWN_POLL_INTERVAL_SECONDS = 2
MLLP_START_OF_BLOCK = 0x0b
MLLP_END_OF_BLOCK = 0x1c
MLLP_CARRIAGE_RETURN = 0x0d
HL7_MSA_ACK_CODE_FIELD = 1
HL7_MSA_ACK_CODE_ACCEPT = b"AA"
ACK = b'MSH|^~\\&|||||20240129093837||ACK|||2.5\rMSA|AA'

raw_data = []
admitted_patient = {}
discharged_patient = []
creatine_results = {}
paged_patient = []
positive_detect = 0
negative_detect = 0
request_count = 0
confusion_matrix = {'TP':0, 'FP':0, 'TN':0, 'FN':0}

async def send_message(pager, message):
    await pager.open_session()
    await pager.parse(message)
    await pager.close_session()


def parse_hl7message(record):
    further_record = record.split('\r')
    if len(further_record) == 3:
        if further_record[0].split('|')[8] == 'ADT^A01':
            pid_record = further_record[1].split('|')
            birthdate = datetime.strptime(pid_record[7], '%Y%m%d')
            current_date = datetime.now()
            age = (current_date.year - birthdate.year -
                   ((current_date.month, current_date.day) < (birthdate.month, birthdate.day)))
            admitted_patient[pid_record[3]] = [age, pid_record[8].lower()]
            return {pid_record[3]: [age, pid_record[8].lower()]}
        else:
            pid_record = further_record[1].split('|')
            discharged_patient.append(pid_record[3])
            return None
    else:
        pid_record = further_record[1].split('|')
        obr_record = further_record[2].split('|')
        obx_record = further_record[3].split('|')
        datetime_str = obr_record[-1]
        formatted_datetime = datetime.strptime(datetime_str, '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
        creatine_results[int(pid_record[-1])] = [admitted_patient[pid_record[-1]][0],
                                                 admitted_patient[pid_record[-1]][1],
                                                 formatted_datetime, round(float(obx_record[-1]), 2)]

        return {int(pid_record[-1]): [admitted_patient[pid_record[-1]][0], admitted_patient[pid_record[-1]][1],
                                      formatted_datetime, round(float(obx_record[-1]), 2)]}


def serve_mllp_dataloader(client, shutdown_mllp, sex_encoder, aki_encoder, clf_model, pager, http_pager, history):
    buffer = b""
    count = 0
    model = Model(sex_encoder, aki_encoder, clf_model)
    r = None
    while not shutdown_mllp.is_set():
        try:
            received = []
            while len(received) < 1:
                r = client.recv(MLLP_BUFFER_SIZE)
                if len(r) == 0:
                    raise Exception("server closed connection")
                buffer += r
                received, buffer = parse_mllp_messages(buffer)
            msg = received[0].decode('ascii')

            result = parse_hl7message(msg)

            if result is not None:
                raw = data_combination_dfAndDict(history, result)
                r = raw
                if not math.isnan(raw.iloc[0]['creatinine_result_0']):
                    feature = preprocess_features(raw)
                    #output = model.run_model(feature)
                    #output = (output[0], [output[1].strip("[]").strip("'")][0])
                    mrn, timestamp, svm_prediction, nhs_prediction = model.run_model(feature)
                    if request_count > 100:
                        request_count = 0
                        positive_detect = 0
                        negative_detect = 0
                    request_count += 1
                    if nhs_prediction == 'y':
                        if svm_prediction == 'y':
                            confusion_matrix['TP'] += 1
                            positive_detect += 1
                            if mrn not in paged_patient:
                                asyncio.run(send_message(http_pager, mrn))
                                print(mrn, ', ', timestamp)
                                paged_patient.append(mrn)
                        else:
                            confusion_matrix['NP'] += 1
                            negative_detect += 1
                    else:
                        negative_detect += 1
                        if svm_prediction == 'y':
                            confusion_matrix['FN'] += 1
                        else:
                            confusion_matrix['TN'] += 1

                    """if output[1] == 'y':
                        if list(result.keys())[0] not in paged_patient:
                            asyncio.run(send_message(http_pager, output))
                            print(list(result.keys())[0], result[list(result.keys())[0]][2])
                            paged_patient.append(list(result.keys())[0])"""


            mllp = bytes(chr(MLLP_START_OF_BLOCK), "ascii")
            mllp += ACK
            mllp += bytes(chr(MLLP_END_OF_BLOCK) + chr(MLLP_CARRIAGE_RETURN), "ascii")
            client.sendall(mllp)
        except Exception as e:
            print(f"mllp: source: closing connection->{e}")
            print(r)
            break
    else:
        print(f"mllp: source: closing connection: mllp shutdown")
    client.close()


def run_mllp_client(host, port, shutdown_mllp, sex_encoder, aki_encoder, clf_model, pager, http_pager, history):
    count = 0
    while not shutdown_mllp.is_set():
        try:
            # Create a socket object using IPv4 and TCP protocol
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            print(f"Successfully connected to {host}:{port}")
            serve_mllp_dataloader(s, shutdown_mllp, sex_encoder, aki_encoder, clf_model, pager, http_pager, history)
        except Exception as e:
            print("fail to connect TCP->connect again")
            continue

    print("mllp: graceful shutdown")


def parse_mllp_messages(buffer):
    i = 0
    messages = []
    consumed = 0
    expect = MLLP_START_OF_BLOCK
    while i < len(buffer):
        if expect is not None:
            if buffer[i] != expect:
                raise Exception(f"source: bad MLLP encoding: want {hex(expect)}, found {hex(buffer[i])}")
            if expect == MLLP_START_OF_BLOCK:
                expect = None
                consumed = i
            elif expect == MLLP_CARRIAGE_RETURN:
                messages.append(buffer[consumed + 1:i - 1])
                expect = MLLP_START_OF_BLOCK
                consumed = i + 1
        else:
            if buffer[i] == MLLP_END_OF_BLOCK:
                expect = MLLP_CARRIAGE_RETURN
        i += 1
    return messages, buffer[consumed:]
