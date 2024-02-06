import pandas as pd 
import numpy as np

"""
Receive a new record, 
check and update the history database, 
then return only the updated or newly added records.
"""
def data_combination_dfAndDict(df, new_data_dict):
    if 'age' not in df.columns:
        df.insert(loc = 1, column = 'age', value = pd.NA)
    if 'sex' not in df.columns:
        df.insert(loc = 2, column = 'sex', value = pd.NA)

    updated_or_newly_added_record = pd.DataFrame()

    for mrn, record in new_data_dict.items(): # Check patient in the new dataset
        age = record[0]
        sex = record[1]
        new_creatinine_date = record[2]
        new_creatinine_result = record[3]
              
        if mrn in df['mrn'].values: # If this is a old patient already in the records, then update the database
            index = df.index[df['mrn'] == mrn][0]
            df.at[index, 'age'] = age
            df.at[index, 'sex'] = sex
            
            i = 0
            while True: # Look for the first available slot for creatinine data
                date_col = f'creatinine_date_{i}'
                result_col = f'creatinine_result_{i}' 
                if date_col not in df.columns: # Create new creatinine date and result columns if not exist
                    df[date_col] = np.nan 
                if result_col not in df.columns:
                    df[result_col] = np.nan
                if pd.isna(df.at[index, date_col]) and pd.isna(df.at[index, result_col]): # Loop until find the available slot
                    df.at[index, date_col] = new_creatinine_date
                    df.at[index, result_col] = new_creatinine_result
                    break
                i += 1
        else: # If this is a new patient, then add to the database
            new_patient_data = pd.Series({
                'mrn': mrn,
                'age': record[0],
                'sex': record[1],
                'creatinine_date_0': record[2],
                'creatinine_result_0': record[3]
            })
            df = pd.concat([df, new_patient_data.to_frame().T], ignore_index = True)
        
        updated_or_newly_added_record = pd.concat([updated_or_newly_added_record, df[df['mrn'] == mrn]])
    
    return updated_or_newly_added_record

def main():
    exist_patient = {16318: [25, 'f', '2024-03-30 13:33:00', 33.33]}
    new_patient = {1111: [30, 'm', '2024-01-11 11:11:00', 11.11]}
    exist_and_new_patient = {16318: [25, 'f', '2024-03-30 13:33:00', 33.33],1111: [30, 'm', '2024-01-11 11:11:00', 11.11]}
    
    history_data_df = pd.read_csv('history.csv')
    df = history_data_df.copy()
    
    # Update exist record(s)
    df_update_exist = data_combination_dfAndDict(df, exist_patient)
    print(df_update_exist)
    
    # Add new record(s)
    df_add_new = data_combination_dfAndDict(df, new_patient)
    print(df_add_new)

    # Update exist record(s) and/or add new record(s)
    df_update_exist_and_add_new = data_combination_dfAndDict(df, exist_and_new_patient)
    print(df_update_exist_and_add_new)

if __name__ == "__main__":
    main()