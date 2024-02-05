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

## Input format required for model

Please ensure that the combined LIMS and PAS data is in the form of the test dataset from coursework 1, i.e a csv, but with the patient's MRN has the first column:

MRN|age|sex|creatinine_date_0|creatinine_result_0|creatinine_date_1|creatinine_result_1

0  | 18| f |       X         |        a          |       Y         |       b

I am currently pulling together a script that processes this to construct the model features, e.g. :

MRN|age|sex|C1_result|RV1|RV2|D |

0  | 18| f |   100.0 | 98|102|33|