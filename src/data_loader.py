import socket
import time
from datetime import datetime

import pandas as pd

from pager import *
from data_processing import data_combination_dfAndDict
from model_feature_construction import preprocess_features
from run_model import Model
import numpy as np
import math
from data_provider import DataProvider
from monitor_application import *
from log_provider import get_logger
import traceback

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
log_flag_send_message = True
log_flag_serve_mllp_dataloader = True
log_flag_run_mllp_client = True
log_flag_parse_mllp_messages = True
log_flag_start_client = True


async def send_message(pager, message, state):
    global log_flag_send_message
    while True:
        try:
            await pager.open_session()
            await pager.parse(message)
            await pager.close_session()
            log_flag_send_message = True
            break
        except IOError as e:
            http_error_received.inc()
            state.set_http_error_count()
            if log_flag_send_message:
                get_logger(__name__).warning(e)
                print(e)
                print(f"HTTP connection failed: {e}")
                print(f"Trying to reconnect... Attempt: {state.get_http_error_count()}")
                log_flag_send_message = False
        except ValueError as e:
            if log_flag_send_message:
                get_logger(__name__).error(e)
                print(e)
                log_flag_send_message = False
            break


def parse_hl7message(record, state):
    further_record = record.split('\r')
    print(f"incoming message: {further_record}")
    if len(further_record) == 3:
        if further_record[0].split('|')[8] == 'ADT^A01':
            pid_record = further_record[1].split('|')
            birthdate = datetime.strptime(pid_record[7], '%Y%m%d')
            current_date = datetime.now()
            age = (current_date.year - birthdate.year -
                   ((current_date.month, current_date.day) < (birthdate.month, birthdate.day)))
            admitted_patient = state.get_admitted_patient()
            admitted_patient[pid_record[3]] = [age, pid_record[8].lower()]
            return {pid_record[3]: [age, pid_record[8].lower()]}
        else:
            pid_record = further_record[1].split('|')
            discharged_patient = state.get_discharged_patient()
            discharged_patient.append(pid_record[3])
            return None
    else:
        pid_record = further_record[1].split('|')
        obr_record = further_record[2].split('|')
        obx_record = further_record[3].split('|')
        datetime_str = obr_record[-1]
        formatted_datetime = datetime.strptime(datetime_str, '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')

        admitted_patient = state.get_admitted_patient()
        if pid_record[-1] not in admitted_patient:
            admitted_patient[pid_record[-1]] = [pd.NA, pd.NA]
        return {int(pid_record[-1]): [admitted_patient[pid_record[-1]][0], admitted_patient[pid_record[-1]][1],
                                      formatted_datetime, round(float(obx_record[-1]), 2)]}


def serve_mllp_dataloader(client, aki_model, http_pager, state):
    global log_flag_serve_mllp_dataloader
    buffer = b""
    r = None
    while True:
        try:
            received = []
            while len(received) < 1:
                r = client.recv(MLLP_BUFFER_SIZE)
                if len(r) == 0:
                    raise Exception("server closed connection")
                buffer += r
                received, buffer = parse_mllp_messages(buffer)

            msg = received[0].decode('ascii')
            result = parse_hl7message(msg, state)
            state.set_request_count()
            messages_received.inc()
            state.set_message_count()
            if result is not None:
                values = list(result.values())
                value = values[0]
                if len(value) == 4:
                    results_distribution.observe(value[-1])
                tests_received.inc()
                state.set_test_count()
                raw = data_combination_dfAndDict(state.get_history(), result)
                if not math.isnan(raw.iloc[0]['creatinine_result_0']):
                    feature = preprocess_features(raw)
                    MRN, aki_result, nhs_result = aki_model.run_ensemble_model(feature)
                    state.set_confusion_matrix(aki_result[0], nhs_result[0])
                    if aki_result[0] == 'y':
                        positive_detection.inc()
                        state.set_positive_detect()
                        if MRN not in state.get_paged_patient():
                            time = result[int(MRN)][2]
                            asyncio.run(send_message(http_pager, (MRN, time, aki_result[0]), state))
                            state.set_paged_patient(MRN)
                    else:
                        state.set_negative_detect()

            mllp = bytes(chr(MLLP_START_OF_BLOCK), "ascii")
            mllp += ACK
            mllp += bytes(chr(MLLP_END_OF_BLOCK) + chr(MLLP_CARRIAGE_RETURN), "ascii")
            client.sendall(mllp)
            log_flag_serve_mllp_dataloader = True
        except Exception as e:
            traceback.print_exc()
            print(f"mllp: source: closing connection->{e}")
            if log_flag_serve_mllp_dataloader:
                get_logger(__name__).warning(f'mllp: source: closing connection->{e}')
                log_flag_serve_mllp_dataloader = False
            break
    client.close()


def run_mllp_client(host, port, aki_model, http_pager, state):
    global log_flag_run_mllp_client
    global log_flag_start_client
    while True:
        try:
            # Create a socket object using IPv4 and TCP protocol
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            if log_flag_start_client:
                get_logger(__name__).info(f"Successfully connected to {host}:{port}")
                log_flag_start_client = False
            # print(f"Successfully connected to {host}:{port}")
            serve_mllp_dataloader(s, aki_model, http_pager, state)
            log_flag_run_mllp_client = True
            log_flag_start_client = True
        except Exception as e:
            reconnection_detection.inc()
            state.set_reconnection_error_count()
            if log_flag_run_mllp_client:
                get_logger(__name__).warning(f'fail to connect TCP->connect again')
                log_flag_run_mllp_client = False
                print("fail to connect TCP->connect again")
            continue


def parse_mllp_messages(buffer):
    global log_flag_parse_mllp_messages
    i = 0
    messages = []
    consumed = 0
    expect = MLLP_START_OF_BLOCK
    while i < len(buffer):
        if expect is not None:
            if buffer[i] != expect:
                if log_flag_parse_mllp_messages:
                    get_logger(__name__).error(f"source: bad MLLP encoding: want {hex(expect)}, found {hex(buffer[i])}")
                    log_flag_parse_mllp_messages = False
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
    log_flag_parse_mllp_messages = True
    return messages, buffer[consumed:]
