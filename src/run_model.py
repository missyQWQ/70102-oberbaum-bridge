import pandas as pd
from sklearn import preprocessing
from sklearn.ensemble import HistGradientBoostingClassifier
#import src.nhs_algorithm as nhs

class Model():
    def __init__(self, sex_encoder, aki_encoder, clf_model):
        self.sex_encoder = sex_encoder
        self.aki_encoder = aki_encoder
        self.clf_model = clf_model

    def run_model(self, data):
        # Encode the sex
        data['sex'] = self.sex_encoder.fit_transform(data['sex'])

        # Make a prediction
        X = data.drop(['mrn'], axis=1)
        prediction = pd.Series(self.clf_model.predict(X.values))

        # Encode aki prediction
        aki_result = str(self.aki_encoder.inverse_transform(prediction))
        MRN = int(data.iloc[0, 0])

        # Return the tuple of (MRN, prediction)
        return (MRN, aki_result)


def run_model(data, model, sex_encoder, aki_encoder):
    """ Runs the gradient boosting model to predict AKI -- pretrained """
    # Encode the sex
    data['sex'] = sex_encoder.fit_transform(data['sex'])

    # Make a prediction
    X = data.drop(['mrn'], axis=1)
    prediction = pd.Series(model.predict(X.values))

    # Encode aki prediction
    aki_result = str(aki_encoder.inverse_transform(prediction))
    MRN = int(data.iloc[0, 0])

    # Return the tuple of (MRN, prediction)
    return (MRN, aki_result)

# class EnsembleModel():
#     """ So we can return both our gradient boost classifier and the NHS algo outcome"""
#     def __init__(self, sex_encoder, aki_encoder, clf_model):
#         self.sex_encoder = sex_encoder
#         self.aki_encoder = aki_encoder
#         self.clf_model = clf_model
    
#     def ensemble_model(self, data):
#         # Encode the sex
#         data['sex'] = self.sex_encoder.fit_transform(data['sex'])

#         # Make a prediction
#         X = data.drop(['mrn'], axis=1)
#         prediction = pd.Series(self.clf_model.predict(X.values))

#         # Encode aki prediction
#         aki_result = str(self.aki_encoder.inverse_transform(prediction))
        
#         # Also get the prediction from the NHS algorithm
#         nhs_result = nhs.run_nhs_algorithm(data)
        
#         MRN = int(data.iloc[0, 0])

#         # Return the tuple of (MRN, cls_prediction, nhs_prediction)
#         return (MRN, aki_result, nhs_result)
        


    