import pandas as pd
import nhs_algorithm as nhs

class Model:
    def __init__(self, clf_model):
        self.clf_model = clf_model

    def run_model(self, data):
        # Directly encode the sex column. Assuming 'f' and 'm' are the possible values.
        data['sex'] = data['sex'].map({'f': 1, 'm': 0})

        # Prepare the data for prediction
        X = data.drop(['mrn'], axis=1)  # Exclude 'mrn' column from features
        predictions = self.clf_model.predict(X.values)

        # As AKI encoding is binary (0 or 1) and direct interpretation is sufficient
        aki_result = ['n' if pred == 0 else 'y' for pred in predictions]
        MRN = int(data.iloc[0, 0])

        # Return a tuple of (MRN, prediction)
        return MRN, aki_result


class EnsembleModel:
    """Enables the combination of gradient boost classifier and NHS algorithm outcomes."""
    
    def __init__(self, clf_model):
        self.clf_model = clf_model

    def run_ensemble_model(self, data):
        # Directly encode the sex column.
        data['sex'] = data['sex'].map({'f': 1, 'm': 0})
        
        # Prepare the data and make prediction
        X = data.drop(['mrn'], axis=1)
        prediction = self.clf_model.predict(X.values)
        aki_result = ['n' if pred == 0 else 'y' for pred in prediction]
        
        # Obtain the NHS algorithm prediction
        nhs_result = nhs.run_nhs_algorithm(data)
        
        MRN = int(data.iloc[0, 0])

        # Return a tuple of (MRN, cls_prediction, nhs_prediction)
        return MRN, aki_result, nhs_result
        


    