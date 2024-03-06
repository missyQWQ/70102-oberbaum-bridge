""" Script to run the NHS algorithm as per https://www.england.nhs.uk/akiprogramme/aki-algorithm/ """
import numpy as np
import pandas as pd
from log_provider import get_logger

def previous_result_mask(df):
    """
    Generates a boolean mask indicating whether each patient has at least one previous result within the last year.

    Args:
        df (pd.DataFrame): DataFrame containing 'RV1' and 'RV2' columns with patient results.

    Returns:
        pd.Series: A boolean Series where True indicates that at least one previous result exists within the last year.

    Raises:
        ValueError: If 'RV1' or 'RV2' columns are missing from the DataFrame.
    """
    required_columns = ['RV1', 'RV2']
    if not all(column in df.columns for column in required_columns):
        get_logger(__name__).error("DataFrame is missing one or more required columns for previous_result_mask: 'RV1', 'RV2'")
        raise ValueError("Input DataFrame does not have the required columns: 'RV1', 'RV2'")

    try:
        data_missing = df[required_columns].isnull().all(axis=1)
        return ~data_missing
    except Exception as e:
        get_logger(__name__).error(f"Error in previous_result_mask: {e}")
        raise


def RV_ratio_mask(df):
    """
    Derives the RV ratios and returns a Series indicating whether the higher of the two ratios is >= 1.5.

    Args:
        df (pd.DataFrame): DataFrame containing the columns 'C1_result', 'RV1', and 'RV2'.

    Returns:
        pd.Series: A boolean Series where True indicates that the higher RV ratio is >= 1.5.

    Raises:
        ValueError: If required columns are missing from the DataFrame.
    """
    try:
        assert set(['C1_result', 'RV1', 'RV2']).issubset(df.columns), "DataFrame missing required columns"
        RV_ratio = df[['C1_result', 'RV1', 'RV2']].copy()
        RV_ratio['RV_ratio_1'] = RV_ratio['C1_result'] / RV_ratio['RV1']
        RV_ratio['RV_ratio_2'] = RV_ratio['C1_result'] / RV_ratio['RV2']
        RV_ratio['higher_RV_ratio'] = np.nanmax(RV_ratio[['RV_ratio_1', 'RV_ratio_2']].values, axis=1)
        RV_ratio['RV_ratio_over_threshold'] = RV_ratio['higher_RV_ratio'] > 1.5
        return pd.Series(RV_ratio['RV_ratio_over_threshold'])
    except AssertionError as error:
        get_logger(__name__).error(f"AssertionError: {error}")
        raise ValueError("Input DataFrame is missing one or more of the required columns: 'C1_result', 'RV1', 'RV2'")
    except Exception as e:
        get_logger(__name__).error(f"Unexpected error in RV_ratio_mask: {e}")
        raise


def D_above_26_mask(df):
    """
    Generates a boolean mask indicating whether the difference 'D' exceeds 26.
    The 'D' value represents the difference between current and lowest previous result within 48hrs

    Args:
        df (pd.DataFrame): DataFrame containing a 'D' column with numeric values.

    Returns:
        pd.Series: A boolean Series where True indicates cases where 'D' exceeds 26.

    Raises:
        ValueError: If the 'D' column is missing from the DataFrame or if it contains non-numeric values which cannot be compared.
    """
    if 'D' not in df.columns:
        get_logger(__name__).error("'D' column is missing from the DataFrame in D_above_26_mask function.")
        raise ValueError("Input DataFrame does not have the required column: 'D'")

    try:
        # Ensure the 'D' column contains numeric values that can be compared
        mask = pd.to_numeric(df['D'], errors='raise') > 26
        return mask
    except ValueError as e:
        get_logger(__name__).error(f"Error converting 'D' column to numeric values in D_above_26_mask: {e}")
        raise ValueError(f"Error in D_above_26_mask due to non-numeric values in 'D' column: {e}")
    except Exception as e:
        get_logger(__name__).error(f"Unexpected error in D_above_26_mask: {e}")
        raise
    

def hit_RV_ratio_threshold(df):
    """
    Determines whether patients meet the RV ratio threshold criteria for AKI detection.

    This function checks two conditions for each patient record:
    - If a previous result is available within the last year (indicated by 'previous_result_available').
    - If the RV ratio exceeds the predefined threshold (indicated by 'RV_ratio_threshold_exceeded').

    Args:
        df (pd.DataFrame): DataFrame with columns 'previous_result_available' and 'RV_ratio_threshold_exceeded'.

    Returns:
        np.ndarray: A boolean array where True indicates patients meeting the RV ratio threshold criteria.

    Raises:
        ValueError: If required columns are missing from the DataFrame.
    """
    required_columns = ['previous_result_available', 'RV_ratio_threshold_exceeded']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        get_logger(__name__).error(f"DataFrame is missing required columns for hit_RV_ratio_threshold: {', '.join(missing_columns)}")
        raise ValueError(f"Input DataFrame does not have the required columns: {', '.join(missing_columns)}")

    try:
        # Compute the logical AND between 'previous_result_available' and 'RV_ratio_threshold_exceeded'
        RV_ratio_test = np.logical_and(
            df['previous_result_available'],
            df['RV_ratio_threshold_exceeded']
        )
        return RV_ratio_test
    except Exception as e:
        get_logger(__name__).error(f"Error in hit_RV_ratio_threshold: {e}")
        raise


def hit_D_threshold(df):
    """
    Determines whether patients meet the D value threshold criteria for AKI detection.

    This function checks two conditions for each patient record:
    - If a previous result is available within the last year (indicated by 'previous_result_available').
    - If the 'D' value exceeds the threshold of 26 (indicated by 'D_above_threshold').

    Args:
        df (pd.DataFrame): DataFrame with columns 'previous_result_available' and 'D_above_threshold'.

    Returns:
        np.ndarray: A boolean array where True indicates patients meeting the D threshold criteria.

    Raises:
        ValueError: If required columns are missing from the DataFrame.
    """
    required_columns = ['previous_result_available', 'D_above_threshold']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        get_logger(__name__).error(f"DataFrame is missing required columns for hit_D_threshold: {', '.join(missing_columns)}")
        raise ValueError(f"Input DataFrame does not have the required columns: {', '.join(missing_columns)}")

    try:
        # Compute the logical AND between 'previous_result_available' and 'D_above_threshold'
        D_threshold_test = np.logical_and(
            df['previous_result_available'],
            df['D_above_threshold']
        )
        return D_threshold_test
    except Exception as e:
        get_logger(__name__).error(f"Error in hit_D_threshold: {e}")
        raise
    

def raise_aki_alert(df):
    """
    Determines whether an AKI alert should be raised based on specific criteria.

    An AKI alert is raised if one of the following conditions is met:
    1. Previous results exist AND the higher RV ratio is >= 1.5.
    2. Previous results exist AND the D value exceeds 26.

    Args:
        df (pd.DataFrame): DataFrame containing 'RV_threshold_breached' and 'D_threshold_breached' columns.

    Returns:
        np.ndarray: A boolean array indicating whether an AKI alert should be raised for each patient.

    Raises:
        ValueError: If required columns are missing from the DataFrame.
    """
    required_columns = ['RV_threshold_breached', 'D_threshold_breached']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        get_logger(__name__).error(f"DataFrame is missing required columns for raise_aki_alert: {', '.join(missing_columns)}")
        raise ValueError(f"Input DataFrame does not have the required columns: {', '.join(missing_columns)}")

    try:
        alert_criteria_met = np.logical_or(
            df['RV_threshold_breached'],
            df['D_threshold_breached']
        )
        return alert_criteria_met
    except Exception as e:
        get_logger(__name__).error(f"Error in raise_aki_alert: {e}")
        raise


def run_nhs_algorithm(df):
    """
    Executes the NHS AKI detection algorithm on a given DataFrame.

    The function adds several intermediate columns to the DataFrame indicating:
    - If a previous result is available.
    - If the RV ratio exceeds the threshold.
    - If the D value exceeds 26.
    It then evaluates these criteria to determine if an AKI alert should be raised.

    Args:
        df (pd.DataFrame): The input DataFrame containing patient results data.

    Returns:
        np.ndarray: An array with 'y' for records where an AKI alert should be raised, and 'n' otherwise.

    Raises:
        Exception: If an error occurs in processing.
    """
    try:
        required_columns = ['RV1', 'RV2', 'C1_result', 'D']  # Example list, adjust based on actual requirements
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"Input DataFrame is missing required columns for running NHS algorithm: {', '.join(missing_columns)}"
            get_logger(__name__).error(error_msg)
            raise ValueError(error_msg)

        # get_logger(__name__).info("Starting NHS algorithm...")
        df['previous_result_available'] = previous_result_mask(df)
        df['RV_ratio_threshold_exceeded'] = RV_ratio_mask(df)
        df['D_above_threshold'] = D_above_26_mask(df)
        df['RV_threshold_breached'] = hit_RV_ratio_threshold(df)
        df['D_threshold_breached'] = hit_D_threshold(df)
        result = np.where(raise_aki_alert(df), 'y', 'n')
        # get_logger(__name__).info("NHS algorithm completed successfully.")
        return result
    except Exception as e:
        get_logger(__name__).error(f"Error running NHS algorithm: {e}")
        raise