import pandas as pd
import pytest
from model_feature_construction import read_and_format_data
from model_feature_construction import format_date_cols

class TestDataIngest:
    """Tests for reading in raw data and formatting column types"""
    
    # Decorator to set up a pre-defined dataset for each test
    def with_dataset(func):
        def wrapper(*args, **kwargs):
            filepath = 'C:/Users/micha/OneDrive/Documents/AI_MSc/SEMLS/70102-oberbaum-bridge/dummy_data.csv'
            data = pd.read_csv(filepath)
            data['id'] = data.index # used for pivoting data  # Replace this with your actual dataset setup
            kwargs['dataset'] = data
            return func(*args, **kwargs)
        return wrapper

    @with_dataset
    def test_date_cols(dataset):
        format_date_cols(dataset)
        
        