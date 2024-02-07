import pytest
import pandas as pd
import sys 
sys.path.append("..") 
from ..data_processing import data_combination_dfAndDict

def test_update_exist_record():
    history_data_df = pd.DataFrame({
        'mrn': [16318],
        'creatinine_date_0': ['2024-01-01 06:12:00'],
        'creatinine_result_0': [16.31]
    })
    exist_patient = {16318: [25, 'f', '2024-03-30 13:33:00', 33.33]}
    df_update_exist = data_combination_dfAndDict(history_data_df, exist_patient)
    assert 16318 in df_update_exist['mrn'].values
    assert 1111 not in df_update_exist['mrn'].values
    assert df_update_exist['age'].values[0] == 25
    assert df_update_exist['sex'].values[0] == 'f'
    assert df_update_exist['creatinine_date_0'].values[0] == '2024-01-01 06:12:00'
    assert df_update_exist['creatinine_result_0'].values[0] == 16.31
    assert df_update_exist['creatinine_date_1'].values[0] == '2024-03-30 13:33:00'
    assert df_update_exist['creatinine_result_1'].values[0] == 33.33

def test_add_new_record():
    history_data_df = pd.DataFrame({
        'mrn': [16318],
        'creatinine_date_0': ['2024-01-01 06:12:00'],
        'creatinine_result_0': [16.31]
    })
    new_patient = {1111: [30, 'm', '2024-01-11 11:11:00', 11.11]}
    df_add_new = data_combination_dfAndDict(history_data_df, new_patient)
    assert 16318 not in df_add_new['mrn'].values
    assert 1111 in df_add_new['mrn'].values
    assert df_add_new['age'].values[0] == 30
    assert df_add_new['sex'].values[0] == 'm'
    assert df_add_new['creatinine_date_0'].values[0] == '2024-01-11 11:11:00'
    assert df_add_new['creatinine_result_0'].values[0] == 11.11

def test_update_exist_and_add_new_records():
    history_data_df = pd.DataFrame({
        'mrn': [16318],
        'creatinine_date_0': ['2024-01-01 06:12:00'],
        'creatinine_result_0': [16.31]
    })
    exist_and_new_patient = {16318: [25, 'f', '2024-03-30 13:33:00', 33.33],
                             1111: [30, 'm', '2024-01-11 11:11:00', 11.11]}
    df_update_exist_and_add_new = data_combination_dfAndDict(history_data_df, exist_and_new_patient)
    assert 16318 in df_update_exist_and_add_new['mrn'].values
    assert 1111 in df_update_exist_and_add_new['mrn'].values
    assert df_update_exist_and_add_new['age'].values[0] == 25
    assert df_update_exist_and_add_new['sex'].values[0] == 'f'
    assert df_update_exist_and_add_new['creatinine_date_0'].values[0] == '2024-01-01 06:12:00'
    assert df_update_exist_and_add_new['creatinine_result_0'].values[0] == 16.31
    assert df_update_exist_and_add_new['creatinine_date_1'].values[0] == '2024-03-30 13:33:00'
    assert df_update_exist_and_add_new['creatinine_result_1'].values[0] == 33.33
    assert df_update_exist_and_add_new['age'].values[1] == 30
    assert df_update_exist_and_add_new['sex'].values[1] == 'm'
    assert df_update_exist_and_add_new['creatinine_date_0'].values[1] == '2024-01-11 11:11:00'
    assert df_update_exist_and_add_new['creatinine_result_0'].values[1] == 11.11
