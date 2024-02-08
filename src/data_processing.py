import pandas as pd 
import numpy as np

"""
Receive a new record, 
check and update the history database, 
then return only the updated or newly added records.
"""
def data_combination_receive_blood_test(df, mrn, record):      
    if mrn in df['mrn'].values: # If this is a old patient already in the records, then update the database
        index = df.index[df['mrn'] == mrn][0]
        df.at[index, 'age'] = record[0]
        df.at[index, 'sex'] = record[1]

        i = 0
        while True: # Look for the first available slot for creatinine data
            date_col = f'creatinine_date_{i}'
            result_col = f'creatinine_result_{i}' 
            if date_col not in df.columns: # Create new creatinine date and result columns if not exist
                df[date_col] = np.nan 
            if result_col not in df.columns:
                df[result_col] = np.nan
            if pd.isna(df.at[index, date_col]) and pd.isna(df.at[index, result_col]): # Loop until find the available slot
                df.at[index, date_col] = record[2]
                df.at[index, result_col] = record[3]
                break
            i += 1
    else: # If this is a new patient, then add to the database
        new_row_idx = df.index.max() + 1 if not df.index.empty else 0
        df.loc[new_row_idx, 'mrn'] = mrn
        df.loc[new_row_idx, 'age'] = record[0]
        df.loc[new_row_idx, 'sex'] = record[1]
        df.loc[new_row_idx, 'creatinine_date_0'] = record[2]
        df.loc[new_row_idx, 'creatinine_result_0'] = record[3]
            
    return df

def data_combination_admit_patient(df, mrn, record):
    if mrn in df['mrn'].values:
        index = df.index[df['mrn'] == mrn][0]
        df.at[index, 'age'] = record[0]
        df.at[index, 'sex'] = record[1]
    else:
        new_row_idx = df.index.max() + 1 if not df.index.empty else 0
        df.loc[new_row_idx, 'mrn'] = mrn
        df.loc[new_row_idx, 'age'] = record[0]
        df.loc[new_row_idx, 'sex'] = record[1]
    
    return df

def data_combination_dfAndDict(df, new_data_dict):
    if 'age' not in df.columns:
        df.insert(loc = 1, column = 'age', value = pd.NA)
    if 'sex' not in df.columns:
        df.insert(loc = 2, column = 'sex', value = pd.NA)
    
    queried_record = pd.DataFrame()
    
    for mrn, record in new_data_dict.items(): 
        if len(record) == 4:
            df = data_combination_receive_blood_test(df, mrn, record)
        elif len(record) == 2:
            df = data_combination_admit_patient(df, mrn, record)
        else:
            raise ValueError("Wrong record. It must in the format 'mrn: [age, sex]' or 'mrn: [age, sex, new_creatinine_date, new_creatinine_result]")
        queried_record = pd.concat([queried_record, df[df['mrn'] == mrn]])
    
    return queried_record

def main():
    history_data_df = pd.read_csv('history.csv')
    df = history_data_df.copy()

# ------------------------- Exist Patient -----------------------------
    patient_exist_admit = {963167: [96, 'm']}
    patient_exist_blood_test = {963167: [10, 'm', '2024-09-06 09:06:00', 96.96]}

    # 1) Admit a patient(has history) to the hospital
    df_admit_exist = data_combination_dfAndDict(df, patient_exist_admit)
    print('1.Admit 963167(has history) to the hospital. Return:')
    print(df_admit_exist.iloc[:, :9])

    # 2) Then insert that patient a new blood test record
    df_receive_blood_exist = data_combination_dfAndDict(df, patient_exist_blood_test)
    print('2.Receive new blood test for 963167. Return:')
    print(df_receive_blood_exist.iloc[:, :9])

# -------------------------- New Patient -------------------------------
    patient_new_admit = {1111: [11, 'm']}
    patient_new_blood_test = {1111: [11, 'm', '2024-01-11 11:11:00', 11.11]}
    patient_new_blood_test_2 = {1111: [11, 'm', '2024-02-21 21:21:00', 21.21]}
    # 1) Admit a patient(new, no history) to the hospital
    df_admit_new = data_combination_dfAndDict(df, patient_new_admit)
    print('1.Admit 1111(new, no history) to the hospital. Return:')
    print(df_admit_new.iloc[:, :9])

    # 2) Then insert that patient a new blood test record
    df_receive_blood_new = data_combination_dfAndDict(df, patient_new_blood_test)
    print('2.Receive new blood test for 1111. Return:')
    print(df_receive_blood_new.iloc[:, :9])

    # 3) Insert that patient a new blood test record again
    df_receive_blood_new = data_combination_dfAndDict(df, patient_new_blood_test_2)
    print('3.Receive one more blood test for 1111. Return:')
    print(df_receive_blood_new.iloc[:, :9])

# ------------------------ Multiple Patients ---------------------------
    multiple_patients_blood_tests = {
        1111: [11, 'm', '2024-01-12 12:12:00', 12.12], 
        963167: [96, 'm', '2024-09-07 09:07:00', 97.97],
        2222: [22, 'f', '2024-02-12 22:22:00', 22.22]
    }
    df_receive_blood_multiple = data_combination_dfAndDict(df, multiple_patients_blood_tests)
    print('Receive multiple blood tests. Return:')
    print(df_receive_blood_multiple.iloc[:, :9])

if __name__ == "__main__":
    main()