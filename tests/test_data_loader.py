from datetime import datetime
from src.data_provider import DataProvider


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
        if pid_record[-1] not in admitted_patient:
            admitted_patient[pid_record[-1]] = [pd.NA, pd.NA]
        return {int(pid_record[-1]): [admitted_patient[pid_record[-1]][0], admitted_patient[pid_record[-1]][1],
                                      formatted_datetime, round(float(obx_record[-1]), 2)]}


def test_parse_hl7_message():
    state = DataProvider()
    hl7_message = 'MSH|^~\&|SIMULATION|SOUTH RIVERSIDE|||20240102135300||ADT^A01|||2.5\rPID|1||497030||ROSCOE DOHERTY||19870515|M\r'
    assert parse_hl7message(hl7_message, state) == {'497030': [36, 'm']}
