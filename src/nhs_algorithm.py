# Functions to run the NHS algorithm
import numpy as np
import pandas as pd

def previous_result_mask(df):
    """ Checks if we have a previous result within 1Y """
    data_missing = df[['RV1', 'RV2']].isnull().all(axis=1)
    return ~data_missing # note the negation


def RV_ratio_mask(df):
    """ Derives the RV ratios and return whether the higher is >=1.5 """
    RV_ratio = df[['C1_result', 'RV1', 'RV2']].copy()
    RV_ratio['RV_ratio_1'] = RV_ratio['C1_result']/RV_ratio['RV1']
    RV_ratio['RV_ratio_2'] = RV_ratio['C1_result']/RV_ratio['RV2']
    RV_ratio['higher_RV_ratio'] = np.nanmax(RV_ratio[['RV_ratio_1', 'RV_ratio_2']].values, axis = 1)
    RV_ratio['RV_ratio_over_threshold'] = RV_ratio['higher_RV_ratio'] > 1.5
    return pd.Series(RV_ratio['RV_ratio_over_threshold'])


def D_above_26_mask(df):
    return df['D'] > 26.
    

def hit_RV_ratio_threshold(df):
    """ Checks case 1 above. """
    RV_ratio_test = np.logical_and(
        df['previous_result_available'],
        df['RV_ratio_threshold_exceeded'])
    return RV_ratio_test


def hit_D_threshold(df):
    """ Checks case 2 above."""
    D_threshold_test = np.logical_and(
        df['previous_result_available'],
        df['D_above_threshold'])
    return D_threshold_test
    

def raise_aki_alert(df):
    """ Send alert if condition at least one condition below hit
    
    According to the algorithm, alerts are sent if:
    1. previous results exist AND higher_RV_ratio >= 1.5
    2. previous results exist AND higher_RV_ratio < 1.5 AND D > 26
    """
    return np.logical_or(df['RV_threshold_breached'],
                         df['D_threshold_breached'])


def run_nhs_algorithm(df):
    df['previous_result_available'] = previous_result_mask(df)
    df['RV_ratio_threshold_exceeded'] = RV_ratio_mask(df)
    df['D_above_threshold'] = D_above_26_mask(df)
    df['RV_threshold_breached'] = hit_RV_ratio_threshold(df)
    df['D_threshold_breached'] = hit_D_threshold(df)
    return np.where(raise_aki_alert(df), 'y', 'n')