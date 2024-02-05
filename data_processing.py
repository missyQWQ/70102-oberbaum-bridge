import pandas as pd 
import numpy as np

def data_combination_dfAndDict(df, new_data_dict):
    df.insert(loc = 1, column = 'age', value = pd.NA)
    df.insert(loc = 2, column = 'sex', value = pd.NA)

    for mrn, record in new_data_dict.items(): # Check patient in the new dataset
        age = record['age']
        sex = record['sex']
        new_creatinine_date = record['creatinine_date']
        new_creatinine_result = record['creatinine_result']
              
        if mrn in df['mrn'].values: # If this is a old patient already in the records, then update the database
            index = df.index[df['mrn'] == mrn][0]
            df.at[index, 'age'] = age
            df.at[index, 'sex'] = sex
            # print(pd.isna(df.at[1, 'creatinine_date_1']))
            # print(pd.isna(df.at[1, 'creatinine_result_1']))
            
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
                'age': record['age'],
                'sex': record['sex'],
                'creatinine_date_0': record['creatinine_date'],
                'creatinine_result_0': record['creatinine_result']
            })
            df = pd.concat([df, new_patient_data.to_frame().T], ignore_index = True)
    return df

def data_combination_pathAndDict(history_data_path, new_data_dict):
    history_data_df = pd.read_csv(history_data_path)
    df = history_data_df.copy()
    df = data_combination_dfAndDict(df, new_data_dict)
    return df

def main():
    new_data_dict = {
        1111: {'age': 30, 'sex': 'm', 'creatinine_date': '2024-01-11 11:11:00', 'creatinine_result': 11.11},
        2222: {'age': 25, 'sex': 'f', 'creatinine_date': '2024-02-22 22:22:00', 'creatinine_result': 22.22},
        16318: {'age': 25, 'sex': 'f', 'creatinine_date': '2024-03-30 13:33:00', 'creatinine_result': 33.33}
    }
    df = data_combination_pathAndDict('history_test.csv', new_data_dict)
    df.to_csv('updated_data.csv', index = False)

if __name__ == "__main__":
    main()