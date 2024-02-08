# 70102-Oberbaum-Bridge

## Package it up!
1. Git pull...
2. Bash from the 70102 directory
3. python3 -m pip install --upgrade pip
4. python3 -m pip install --upgrade build
5. python3 -m build

That will build the package. (See https://packaging.python.org/en/latest/tutorials/packaging-projects/)

Then run "pip install -e ." which will install the package in "editable" mode

From there, you can just run "pytest" or specific tests e.g. "pytest tests/test_feature_construction.py" for example.

Happy testing ^_^

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
1. data_combination_dfAndDict(df, new_data_dict)
Given database(DataFrame) and newly received record(dict), return a new DataFrame contains all the information about that queried patient.
2. data_combination_receive_blood_test(df, mrn, record)
Receive a new blood test record, tell if the patient if already exist in the database or not,
- if exist, update database with the newly received record and return this patient's basic information as well as all blood test records
- if not exist, insert this new blood record together with this patient's basic information to the database and return them
3. data_combination_admit_patient(df, mrn, record)
Receive a patient admitting record, tell if the patient if already exist in the database or not,
- if exist, return this patient's basic information as well as all blood test records
- if not exist, insert this patient's basic information to the database and return them

0. History Database Format
```
mrn  |creatinine_date_0    |creatinine_result_0|creatinine_date_1|creatinine_result_1|...
16318|'2024-01-01 06:12:00'|       16.31       |       NAN       |        NAN        |...
```
1. Admit a patient
```
# Input
admit_patient = {16318: [25, 'f']}
# Output
mrn  |creatinine_date_0    |creatinine_result_0|creatinine_date_1|creatinine_result_1|...
16318|'2024-01-01 06:12:00'|       16.31       |       NAN       |        NAN        |...
```
2. Add a record
```
# Input format
add_record = {16318: [25, 'f', '2024-03-30 13:33:00', 33.33]}
# Output format
mrn  |age|sex|creatinine_date_0    |creatinine_result_0|creatinine_date_1    |creatinine_result_1|...
16318|25 |'f'|'2024-01-01 06:12:00'|       16.31       |'2024-03-30 13:33:00'|       33.33       |...
```
3. Add multiple records
```
# Input format
add_records = {
    16318: [25, 'f', '2024-03-30 13:33:00', 33.33],
    1111: [30, 'm', '2024-01-11 11:11:00', 11.11]
}
# Output format
mrn  |age|sex|creatinine_date_0    |creatinine_result_0|creatinine_date_1    |creatinine_result_1|...
16318|25 |'f'|'2024-01-01 06:12:00'|       16.31       |'2024-03-30 13:33:00'|       33.33       |...
1111 |30 |'m'|'2024-01-11 11:11:00'|       11.11       |       NAN           |        NAN        |...
```