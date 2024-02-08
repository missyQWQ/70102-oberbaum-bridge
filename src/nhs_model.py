from datetime import datetime, timedelta
import statistics

# global flag variables for outputs of AKI predictions
AKI1 = 'y'
AKI2 = 'y'
AKI3 = 'y'
NO_FLAG = 'n'
FLAG_LOW = 'n'
FLAG_HIGH = 'n'


def preprocess(patient):
    """
       Preprocess the patient data into a dictionary in the format:
       patient_info:
       {
       'age': age(int),
       'gender': gender(str),
       'c1': the most recent creatine result(float),
       't_c1': time to make the most recent creatine result(datetime),
       'pr': the previous creatine result before c1(float),
       't_pr': time to make the previous creatine result(datetime),
       'other_results': all creatine results from the patient(list(float)),
       'rv_ratio': rv_ratio(float)
       }

       Parameters:
       patient (list): list of patient's information

       Returns:
       int: The sum of the two numbers.
    """
    # print(patient)
    patient_info = {}
    patient = [element for element in patient if element]
    patient_info['age'] = int(patient[0])
    patient_info['gender'] = patient[1]
    patient_info['c1'] = float(patient[-1])
    patient_info['t_c1'] = datetime.strptime(patient[-2], '%Y-%m-%d %H:%M:%S')
    if len(patient) == 4 or len(patient) == 5:
        patient_info['pr'] = float(patient[-1])
        patient_info['t_pr'] = datetime.strptime(patient[-2], '%Y-%m-%d %H:%M:%S')
    else:
        patient_info['pr'] = float(patient[-3])
        patient_info['t_pr'] = datetime.strptime(patient[-4], '%Y-%m-%d %H:%M:%S')

    if patient[2] != 'y' and patient[2] != 'n':
        patient_info['other_results'] = [float(result) for result in patient[3::2]]
    else:
        patient_info['other_results'] = [float(result) for result in patient[4::2]]
        patient_info['aki'] = patient[2]
    patient_info['rv_ratio'] = -1.0
    return patient_info


def model(patient, ri_table):
    """
       make the prediction based on patient's information and ri_table

       Parameters:
       patient (list): list of patient's information,
       ri_table (pandas DataFrame)

       Returns:
       str: 'y' or 'n'
    """
    patient_info = preprocess(patient)
    ri_low, ri_high = -1, -1
    if patient_info['age'] <= 12:
        ri_low = ri_table[ri_table['Age'] == patient_info['age']]['Low'].iloc[0]
        ri_high = ri_table[ri_table['Age'] == patient_info['age']]["High"].iloc[0]
    elif patient_info['age'] < 17:
        ri_low = ri_table[(ri_table['Age'] == patient_info['age']) &
                          (ri_table['Gender'] == patient_info['gender'])]['Low'].iloc[0]
        ri_high = ri_table[(ri_table['Age'] == patient_info['age']) &
                           (ri_table['Gender'] == patient_info['gender'])]['High'].iloc[0]
    else:
        ri_low = ri_table[(ri_table['Gender'] == patient_info['gender']) &
                          (ri_table['Age'] == 17)]['Low'].iloc[0]
        ri_high = ri_table[(ri_table['Age'] == 17) &
                           (ri_table['Gender'] == patient_info['gender'])]['High'].iloc[0]
    year_time = timedelta(days=365)
    week_time = timedelta(days=7)
    two_days_time = timedelta(days=2)
    retest_duration = patient_info['t_c1'] - patient_info['t_pr']
    if retest_duration > year_time:
        if patient_info['c1'] < ri_low:
            return FLAG_LOW
        elif patient_info['c1'] <= ri_high:
            return NO_FLAG
        else:
            return FLAG_HIGH
    else:
        if retest_duration <= week_time:
            rv1 = min(patient_info['other_results'])
            patient_info['rv_ratio'] = patient_info['c1'] / rv1
        else:
            rv2 = statistics.median(patient_info['other_results'])
            patient_info['rv_ratio'] = patient_info['c1'] / rv2

    if patient_info['rv_ratio'] >= 1.5:
        if patient_info['age'] < 18:
            if patient_info['c1'] > 3 * ri_high:
                return AKI3
        else:
            if patient_info['c1'] > 354:
                return AKI3

        if patient_info['rv_ratio'] >= 3.0:
            return AKI3
        elif patient_info['rv_ratio'] >= 2.0:
            return AKI2
        else:
            return AKI1
    else:
        if retest_duration <= two_days_time:
            if patient_info['c1'] - patient_info['pr'] > 26:
                return AKI1
            else:
                return NO_FLAG
        else:
            return NO_FLAG