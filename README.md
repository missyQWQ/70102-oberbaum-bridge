# 70102-Oberbaum-Bridge

## Output Format for Data Processing
1. Admitted Patient(dict)
2. discharged_patient(list)
3. creatine_results(dict)
```
# example
admitted_patient = {
    PID:[MRN, DOB, GENDER]
}

discharged_patient = [MRN_1, MRN_2]

creatine_results = {
    PID:[AGE, SEX, TEST_DATE, RESULT]
}
```
## Data Processing
1. data_combination_pathAndDict(file_path, dict)
```
# Input
1. file_path: The path of history.csv
2. dict: New patient data, for example,
creatine_results = {
    PID:[AGE, SEX, TEST_DATE, RESULT]
}
# Output
DataFrame for the model:
MRN|age|sex|creatinine_date_0|creatinine_result_0|creatinine_date_1|creatinine_result_1|...
0  | 18| 'f' | '2024-01-01 06:12:00' |   11.11   | 'yyyy-mm-dd hh:mm:ss' |    12.12    |...
```
2. data_combination_dfAndDict(DataFrame, dict)
```
# Input
1. DataFrame: The DataFrame of history data, for example
MRN|creatinine_date_0|creatinine_result_0|creatinine_date_1|creatinine_result_1|...
0  | '2024-01-01 06:12:00' |   11.11   | 'yyyy-mm-dd hh:mm:ss' |    12.12    |...
2. dict: New patient data, for example,
creatine_results = {
    PID:[AGE, SEX, TEST_DATE, RESULT]
}
# Output
DataFrame for the model:
MRN|age|sex|creatinine_date_0|creatinine_result_0|creatinine_date_1|creatinine_result_1|...
0  | 18| 'f' | '2024-01-01 06:12:00' |   11.11   | 'yyyy-mm-dd hh:mm:ss' |    12.12    |...
```

## Input format required for model

Please ensure that the combined LIMS and PAS data is in the form of the test dataset from coursework 1, i.e a csv, but with the patient's MRN has the first column:

MRN|age|sex|creatinine_date_0|creatinine_result_0|creatinine_date_1|creatinine_result_1

0  | 18| f |       X         |        a          |       Y         |       b

I am currently pulling together a script that processes this to construct the model features, e.g. :

MRN|age|sex|C1_result|RV1|RV2|D |

0  | 18| f |   100.0 | 98|102|33|