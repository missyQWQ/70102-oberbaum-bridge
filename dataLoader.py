import argparse
import socket
import threading
import time
from datetime import datetime

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


def parse_hl7message(data):
    for record in data:
            further_record = record.split('\r')
            if len(further_record) == 3:
                if further_record[0].split('|')[8] == 'ADT^A01':
                    pid_record = further_record[1].split('|')
                    birthdate = datetime.strptime(pid_record[7], '%Y%m%d')
                    current_date = datetime.now()
                    age = (current_date.year - birthdate.year -
                           ((current_date.month, current_date.day) < (birthdate.month, birthdate.day)))
                    admitted_patient[pid_record[3]] = [age, pid_record[8].lower()]
                else:
                    pid_record = further_record[1].split('|')
                    discharged_patient.append(pid_record[3])
            else:
                pid_record = further_record[1].split('|')
                obr_record = further_record[2].split('|')
                obx_record = further_record[3].split('|')
                datetime_str = obr_record[-1]
                formatted_datetime = datetime.strptime(datetime_str, '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
                creatine_results[int(pid_record[-1])] = [admitted_patient[pid_record[-1]][0], admitted_patient[pid_record[-1]][1],
                                                    formatted_datetime, round(float(obx_record[-1]), 2)]


def serve_mllp_dataloader(client, shutdown_mllp):
    buffer = b""
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
            raw_data.append(msg)

            mllp = bytes(chr(MLLP_START_OF_BLOCK), "ascii")
            mllp += ACK
            mllp += bytes(chr(MLLP_END_OF_BLOCK) + chr(MLLP_CARRIAGE_RETURN), "ascii")
            client.sendall(mllp)
        except Exception as e:
            print(f"mllp: source: closing connection->{e}")
            break
    else:
        print(f"mllp: source: closing connection: mllp shutdown")
    client.close()


def run_mllp_client(host, port, shutdown_mllp):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((host, port))
        s.settimeout(SHUTDOWN_POLL_INTERVAL_SECONDS)
        print(f"mllp: listening on {host}:{port}")
        source = f"{host}:{port}"
        print(f"mllp: {source}: make a connection")
        serve_mllp_dataloader(s, shutdown_mllp)
        parse_hl7message(raw_data)
        print(creatine_results)
        while not shutdown_mllp.is_set():
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mllp", default=8440, type=int, help="Port on which to replay HL7 messages via MLLP")
    flags = parser.parse_args()
    shutdown_mllp = threading.Event()
    # t = threading.Thread(target=run_mllp_client, args=("0.0.0.0", flags.mllp, shutdown_mllp), daemon=True)

    #t.start()
    #t.join()
    run_mllp_client("0.0.0.0", flags.mllp, shutdown_mllp)
    print("Work Done!!!!!")


if __name__ == "__main__":
    main()
