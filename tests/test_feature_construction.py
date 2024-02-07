import pytest
import pandas as pd 
from src.model_feature_construction import *

def dataset(func):
    def wrapper(*args, **kwargs):
        data = pd.read_csv('src/history.csv')
        data = pd.DataFrame(data)
        return func(data=data, *args, **kwargs)
    return wrapper
    

class TestDataTypeCoercion:
    
    @dataset
    def test_date_cols(self, data):
        """ Tests that all _date_ columns are of type datetime.
        It does NOT check that all columns that should be datetime are so. """
        format_date_cols(data)
        data = data.select_dtypes(include=['datetime'])
        assert all(['_date_' in x for x in list(data.columns)])
        
    @dataset
    def test_result_cols(self, data):
        """ Tests that all _result_ columns are of type numeric."""
        format_date_cols(data)
        results_cols = [col for col in data.columns if '_result_' in col]
        data = data[results_cols]
        assert (data.dtypes == 'float64').all()
        
        
        