import socket
import time
from datetime import datetime
from pager import *
from data_processing import data_combination_dfAndDict
from model_feature_construction import preprocess_features
from run_model import Model
import numpy as np
import math
from data_provider import DataProvider

from src.log_provider import get_logger

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


async def send_message(pager, message, state):
    while True:
        try:
            await pager.open_session()
            await pager.parse(message)
            await pager.close_session()
            break
        except IOError as e:
            state.set_http_error_count()
            print(f"HTTP connection failed: {e}")
            print(f"Trying to reconnect... Attempt: {state.get_http_error_count()}")
        except ValueError as e:
            print(f"Pager {e} found")
            break


def parse_hl7message(record, state):
    further_record = record.split('\r')
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

        return {int(pid_record[-1]): [admitted_patient[pid_record[-1]][0], admitted_patient[pid_record[-1]][1],
                                      formatted_datetime, round(float(obx_record[-1]), 2)]}


def serve_mllp_dataloader(client, aki_model, http_pager, state):
    buffer = b""
    r = None
    state = DataProvider()
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
            state.set_message_count()
            if result is not None:
                state.set_test_count()
                raw = data_combination_dfAndDict(state.get_history(), result)
                if not math.isnan(raw.iloc[0]['creatinine_result_0']):
                    feature = preprocess_features(raw)
                    MRN, aki_result, nhs_result = aki_model.run_ensemble_model(feature)
                    state.set_confusion_matrix(aki_result, nhs_result)
                    if aki_result == 'y':
                        state.set_positive_detect()
                        if MRN not in state.get_paged_patient():
                            time = result[int(MRN)][2]
                            asyncio.run(send_message(http_pager, (MRN, time), state))
                            print(f'MRN: {MRN}, time: {time}')
                            # paged_patient.append(list(result.keys())[0])
                            state.set_paged_patient(MRN)
                    else:
                        state.set_negative_detect()

            mllp = bytes(chr(MLLP_START_OF_BLOCK), "ascii")
            mllp += ACK
            mllp += bytes(chr(MLLP_END_OF_BLOCK) + chr(MLLP_CARRIAGE_RETURN), "ascii")
            client.sendall(mllp)
        except Exception as e:
            print(f"mllp: source: closing connection->{e}")
            print(r)
            get_logger(__name__).warning(f'mllp: source: closing connection->{e}')
            break
    client.close()


def run_mllp_client(host, port, aki_model, http_pager, state):
    while True:
        try:
            # Create a socket object using IPv4 and TCP protocol
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            print(f"Successfully connected to {host}:{port}")
            serve_mllp_dataloader(s, aki_model, http_pager, state)
        except Exception as e:
            state.set_reconnection_error_count()
            get_logger(__name__).warning(f'fail to connect TCP->connect again')
            print("fail to connect TCP->connect again")
            continue

    print("mllp: graceful shutdown")
    get_logger(__name__).warning(f'mllp: graceful shutdown')


def parse_mllp_messages(buffer):
    i = 0
    messages = []
    consumed = 0
    expect = MLLP_START_OF_BLOCK
    while i < len(buffer):
        if expect is not None:
            if buffer[i] != expect:
                get_logger(__name__).error(f"source: bad MLLP encoding: want {hex(expect)}, found {hex(buffer[i])}")
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
