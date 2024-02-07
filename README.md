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
data_combination_dfAndDict(DataFrame, dict): Receive a new record, check and update the history database, then return only the updated or newly added records.

* History Database Format
```
mrn  |creatinine_date_0    |creatinine_result_0|creatinine_date_1|creatinine_result_1|...
16318|'2024-01-01 06:12:00'|       16.31       |       NAN       |        NAN        |...
```
1. Update exist record
```
# Input format
exist_patient = {
    16318: [25, 'f', '2024-03-30 13:33:00', 33.33]
}
# Output format
mrn  |age|sex|creatinine_date_0    |creatinine_result_0|creatinine_date_1    |creatinine_result_1|...
16318|25 |'f'|'2024-01-01 06:12:00'|       16.31       |'2024-03-30 13:33:00'|       33.33       |...
```
2. Add new record
```
# Input format
new_patient = {
    1111: [30, 'm', '2024-01-11 11:11:00', 11.11]
}
# Output format
mrn |age|sex|creatinine_date_0    |creatinine_result_0|creatinine_date_1|creatinine_result_1|...
1111|30 |'m'|'2024-01-11 11:11:00'|       11.11       |       NAN       |        NAN        |...
```
3. Update one or multiple exist records and/or add one or multiple new records
```
# Input format
exist_and_new_patient = {
    16318: [25, 'f', '2024-03-30 13:33:00', 33.33],
    1111: [30, 'm', '2024-01-11 11:11:00', 11.11]
}
# Output format
mrn  |age|sex|creatinine_date_0    |creatinine_result_0|creatinine_date_1    |creatinine_result_1|...
16318|25 |'f'|'2024-01-01 06:12:00'|       16.31       |'2024-03-30 13:33:00'|       33.33       |...
1111 |30 |'m'|'2024-01-11 11:11:00'|       11.11       |       NAN           |        NAN        |...
```