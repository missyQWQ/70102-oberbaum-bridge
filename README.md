# 70102-Oberbaum-Bridge
An Acute Kidney Injury (AKI) Prediction and Alert System.
It's a university project from Imperial College London 2023/24 70102 Software Engineering for Machine Learning Systems.
Supervisor: Andrew Eland
Autoher: Michael-Hollins, Peter Wang, Yiyuan Wang, Yichun Zhang
## Introduction
AKI prediction application will read MLLP message from hosptial and predict AKI test. 
If the prediction is positive, we will send patient information to hosptial pager system via HTTP.
## Structure
```bash
.
├── Dockerfile # To build docker image for AKI prediction application
├── LICENSE.txt
├── README.md
├── __init__.py # init file for package
├── coursework4.yaml # yaml file to deploy to kubernete
├── draft_post_morterm.docx # Postmortem in real environment
├── main.sh # bash script to start application in kubernete
├── pyproject.toml # file for package
├── requirements.txt # dependency needed
├── src
│   ├── AKI_ALERT_mdh323.egg-info # for Package
│   ├── aki.csv # ground true results for development
│   ├── clf_model.pkl # pickle file storing model
│   ├── data_loader.py # functions to make connection with TCP and parse info 
│   ├── data_processing.py # process info for model
│   ├── data_provider.py # class to store important data for application
│   ├── history.csv # history info for development
│   ├── log_provider.py # create a log for application
│   ├── main.py # main file to run application
│   ├── messages.mllp # message flow for development
│   ├── model_feature_construction.py # further process info for model
│   ├── monitor_application.py # Promethus Client class 
│   ├── nhs_algorithm.py # nhs algorithm for AKI prediction
│   ├── pager.py # HTTP functions to send to pager system
│   ├── run_model.py # run model here
│   ├── run_model_for_testing.py # run model in fake info for test
│   ├── simulator.py # hosptial simulator system for development
│   └── state # directory for storing log and important info locally
└── tests # directory for unit tests
```
## Run it!!
### Local Machine
```bash
python3 main.py --history=history.csv --MLLP_ADDRESS='0.0.0.0:8440' --PAGER_ADDRESS='0.0.0.0:8441'
python3 simulator.py
```
### Docker
```bash
docker build -t coursework3 .
docker run -v yourpath/state:/state -p 8000:8000 --env MLLP_ADDRESS=host.docker.internal:8440 --env PAGER_ADDRESS=host.docker.internal:8441 coursework3      
python3 simulator.py
```

## Package it up!
```bash
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade build
python3 -m build
```
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
