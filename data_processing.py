import pandas as pd 

def data_combination_dfAndDict(df, new_data_dict):
    df.insert(loc = 1, column = 'age', value = pd.NA)
    df.insert(loc = 2, column = 'sex', value = pd.NA)

    for mrn, record in new_data_dict.items():
        age = record['age']
        sex = record['sex']
        new_creatinine_date = record['creatinine_date']
        new_creatinine_result = record['creatinine_result']
        
        if mrn in df['mrn'].values:
            index = df.index[df['mrn'] == mrn][0]
            df.at[index, 'age'] = age
            df.at[index, 'sex'] = sex

    return df

def data_combination_pathAndDict(history_data_path, new_data_dict):
    history_data_df = pd.read_csv(history_data_path)
    df = history_data_df.copy()
    # new_data_df = pd.DataFrame(new_data_dict)
    # new_data_df = pd.DataFrame.from_dict(new_data_dict, orient='index').reset_index().rename(columns={'index': 'mrn'})
    # print(history_data_df)
    # print('----------------')
    # print(new_data_df)
    df = data_combination_dfAndDict(df, new_data_dict)
    return df

def main():
    new_data_dict = {
        1111: {'age': 30, 'sex': 'm', 'creatinine_date': '2024-01-11 11:11:00', 'creatinine_result': 11.11},
        2222: {'age': 25, 'sex': 'f', 'creatinine_date': '2024-02-22 22:22:00', 'creatinine_result': 22.22},
        16318: {'age': 25, 'sex': 'f', 'creatinine_date': '2024-03-30 13:33:00', 'creatinine_result': 33.33}
    }
    df = data_combination_pathAndDict('history2.csv', new_data_dict)
    # print(df)
    df.to_csv('updated_data.csv', index = False)

if __name__ == "__main__":
    main()