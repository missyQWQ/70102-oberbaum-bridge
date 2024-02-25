import pandas as pd
import pickle
from sklearn import preprocessing
from sklearn.ensemble import HistGradientBoostingClassifier
from model_feature_construction import *
import time

running_model_times = []

t0 = time.time()
def run_model(data, model, sex_encoder, aki_encoder):
    """ Runs the gradient boosting model to predict AKI -- pretrained """
    # Encode the sex
    data['sex'] = sex_encoder.fit_transform(data['sex'])
    t1 = time.time()
    print("Encoding sex", t1-t0)
    # Make a prediction
    X = data.drop(['mrn'], axis = 1)
    t2 = time.time()
    print("Dropping MRN", t2-t1)
    prediction = model.predict(X.values)
    t3 = time.time()
    print("Predicting using model", t3-t2)
    prediction = pd.Series(prediction)
    t4 = time.time()
    print("Prediction into pd Series", t4-t3)
    # Encode aki prediction
    aki_result = str(aki_encoder.inverse_transform(prediction))
    t5 = time.time()
    print("Encoding AKI prediction", t5-t4)
    MRN = int(data.iloc[0, 0])
    t6 = time.time()
    print("Retreiving MRN", t6-t5)
    # Return the tuple of (MRN, prediction)
    running_model_times.append(t3-t2)
    return (MRN, aki_result)

base_dir = 'C:/Users/micha/OneDrive/Documents/AI_MSc/coursework/SEMLS/coursework_1_submission/'
with open(base_dir + 'sex_encoder_model.pkl', "rb") as file:
    sex_encoder = pickle.load(file)
with open(base_dir + 'aki_encoder_model.pkl', "rb") as file:
    aki_encoder = pickle.load(file)    
with open(base_dir + 'clf_model.pkl', "rb") as file:
    clf_model = pickle.load(file)

test_message = pd.DataFrame.from_dict( 
                            {'mrn': [322445],
                              'age': [29],
                              'sex': ['f'],
                              'creatinine_date_0': ['2023-10-12 16:14:00'],
                              'creatinine_result_0': [125.72],
                              'creatinine_date_1': ['2023-10-22 13:17:00'],
                              'creatinine_result_1': [148.49],
                              'creatinine_date_2': ['2023-10-23 12:39:00'],
                              'creatinine_result_2': [142.47],
                              'creatinine_date_3': ['2023-10-24 16:36:00'],
                              'creatinine_result_3': [151.89]})

test_message = preprocess_features(test_message)

result = run_model(test_message, model = clf_model, sex_encoder=sex_encoder, aki_encoder=aki_encoder)
result = run_model(test_message, model = clf_model, sex_encoder=sex_encoder, aki_encoder=aki_encoder)
result = run_model(test_message, model = clf_model, sex_encoder=sex_encoder, aki_encoder=aki_encoder)
result = run_model(test_message, model = clf_model, sex_encoder=sex_encoder, aki_encoder=aki_encoder)
result = run_model(test_message, model = clf_model, sex_encoder=sex_encoder, aki_encoder=aki_encoder)
result = run_model(test_message, model = clf_model, sex_encoder=sex_encoder, aki_encoder=aki_encoder)
result = run_model(test_message, model = clf_model, sex_encoder=sex_encoder, aki_encoder=aki_encoder)
result = run_model(test_message, model = clf_model, sex_encoder=sex_encoder, aki_encoder=aki_encoder)
result = run_model(test_message, model = clf_model, sex_encoder=sex_encoder, aki_encoder=aki_encoder)