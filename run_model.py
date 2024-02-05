import pandas as pd
from sklearn import preprocessing
from sklearn.ensemble import HistGradientBoostingClassifier

def run_model(data, model, sex_encoder, aki_encoder):
    """ Runs the gradient boosting model to predict AKI -- pretrained """
    # Encode the sex
    data['sex'] = sex_encoder.fit_transform(data['sex'])
    
    # Make a prediction
    X = data.drop(['mrn'], axis = 1)
    prediction = pd.Series(model.predict(X.values))
    
    # Encode aki prediction
    aki_result = str(aki_encoder.inverse_transform(prediction))
    MRN = int(data.iloc[0, 0])
    
    # Return the tuple of (MRN, prediction)
    return (MRN, aki_result)