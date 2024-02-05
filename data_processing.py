import pandas as pd 
import numpy as np

def data_combination_dfAndDict(df, new_data_dict):
    df.insert(loc = 1, column = 'age', value = pd.NA)
    df.insert(loc = 2, column = 'sex', value = pd.NA)

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
    return df

def data_combination_pathAndDict(history_data_path, new_data_dict):
    history_data_df = pd.read_csv(history_data_path)
    df = history_data_df.copy()
    df = data_combination_dfAndDict(df, new_data_dict)
    return df

def main():
    new_data_dict = {
        1111: [30, 'm', '2024-01-11 11:11:00', 11.11],
        2222: [25, 'f', '2024-02-22 22:22:00', 22.22],
        16318: [25, 'f', '2024-03-30 13:33:00', 33.33]
    }
    df = data_combination_pathAndDict('history.csv', new_data_dict)
    print(df)

if __name__ == "__main__":
    main()