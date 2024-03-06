import numpy as np
import pandas as pd
import logging

"""
Purpose of script: To transform input of the form 

MRN|age|sex|creatinine_date_0|creatinine_result_0|creatinine_date_1|creatinine_result_1
 0 | 18| f |       X         |        a          |       Y         |       b

into what the model needs: 
    - the NHS algoritm variables (RV1, RV2, D) 
    - the data in long format
    
MRN|age|sex|C1_result|RV1|RV2|D |
 0 | 18| f |   100.0 | 98|102|33|
"""


""" Step 1: Make sure the raw data is of the correct type """

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Dates
def format_date_cols(data):
    """Finds and formats all date columns into %Y-%m-%d %H:%M:%S"""
    try:
        date_cols = data.filter(like='_date_').columns
        for date_col in date_cols:
            data[date_col] = pd.to_datetime(data[date_col], format='%Y-%m-%d %H:%M:%S')
        return True
    except ValueError as e:
        logging.error(f"Date formatting error in column {date_col}: {e}")
        return False

# Numerical results
def format_result_cols(data):
    """Coerces all creatinine result features into type float"""
    try:
        result_cols = data.filter(like='_result_').columns
        for result_col in result_cols:
            data[result_col] = pd.to_numeric(data[result_col], errors='raise')
        return True
    except ValueError as e:
        logging.error(f"Numeric formatting error in column {result_col}: {e}")
        return False

# Patient information
def format_other_cols(data):
    """Coerces other column data types to how we would expect"""
    try:
        data['age'] = pd.to_numeric(data['age'], errors='raise')
        data['mrn'] = pd.to_numeric(data['mrn'], errors='raise')
        data['sex'] = data['sex'].astype('string')
        return True
    except ValueError as e:
        logging.error(f"Error formatting patient information: {e}")
        return False

def format_col_types(data):
    """Wrapper function to call all column type casting/formatting"""
    if not format_date_cols(data):
        logging.info("Dates couldn't be formatted correctly - check raw data")
    if not format_result_cols(data):
        logging.info("Results couldn't be formatted into numeric - check raw data")
    if not format_other_cols(data):
        logging.info("Patient information failed to be formatted - check raw data")


""" Step 2: Melt data into long format """        
                
def consolidate_tests(df):
    """
    Takes observation of patients and melts into long format.
    
    For example, 
    mrn|creatinine_date_0|creatinine_result_0|creatinine_date_1|creatinine_result_1
     0 |        X        |        a          |       Y         |       b
    into:
    mrn| date | result |
     0 |  X   |   a    |
     0 |  Y   |   b    | 
    
    Args:
        df (pd.DataFrame): Dataframe from which an observation is selected.
        
    Returns:
        pd.DataFrame: Observation i but with dates and results columns.
        
    Raises:
        ValueError: If the input dataframe does not contain expected columns.
    """
    id_cols = ['mrn', 'age', 'sex']
    
    try:
        # Validate presence of expected columns in df
        if not all(col in df.columns for col in id_cols):
            raise ValueError(f"Input dataframe missing one of the required id columns: {id_cols}")

        df_long = df.melt(id_vars=id_cols)
        df_long = df_long.dropna(subset=['value'])
        df_long['test'] = df_long['variable'].str.split('_').str[-1]
        df_long['variable'] = df_long['variable'].str.split('_').str[1]
        df_wide = df_long.pivot_table(index=id_cols + ['test'],
                                      columns='variable',
                                      values='value',
                                      aggfunc='first').reset_index()
        logging.info("Data reshaped successfully")
        return df_wide
    except Exception as e:
        logging.error(f"Data reshaping failed: {e}")
        raise ValueError(f"Data reshaping failed due to an error: {e}")


""" Step 3: Construct the features used in the NHS AKI algorithm
Reference: https://www.england.nhs.uk/akiprogramme/aki-algorithm/ """  

def get_time_masks(df):
    """
    Returns various boolean masks depending on the timeframe of observation.

    Args:
        df (pd.DataFrame): DataFrame with a 'time_since_C1' column representing time since a specific event.

    Returns:
        tuple of np.ndarray: Three boolean arrays representing different timeframes:
                             - within_7_days,
                             - within_48h,
                             - within_8_to_365_days.

    Raises:
        ValueError: If 'time_since_C1' column is missing or if an unexpected data type is encountered.
    """
    try:
        if 'time_since_C1' not in df.columns:
            raise KeyError("Column 'time_since_C1' is missing from the input DataFrame.")
        
        within_48h = np.logical_and(
            df['time_since_C1'] > pd.Timedelta(value=-48, unit='hours'),
            df['time_since_C1'] < pd.Timedelta(value=0)
        )
        
        within_8_to_365_days = np.logical_and(
            df['time_since_C1'] > pd.Timedelta(value=-366, unit='days'),
            df['time_since_C1'] < pd.Timedelta(value=-8, unit='days'),
        )
        
        within_7_days = np.logical_and(
            df['time_since_C1'] > pd.Timedelta(value=-8, unit='days'),
            df['time_since_C1'] < pd.Timedelta(value=0)
        )

        return within_7_days, within_48h, within_8_to_365_days
    except KeyError as e:
        logging.error(f"KeyError - {e}")
        raise ValueError(f"KeyError - {e}")
    except Exception as e:
        logging.error(f"Failed to construct time masks due to an unexpected error: {e}")
        raise ValueError(f"Failed to construct time masks due to an unexpected error: {e}")


def adjust_duplicate_dates(df):
    """
    Adjust dates for duplicate entries by adding a minute to the last duplicate.
    """
    duplicates_mask = df.duplicated(subset=['mrn', 'date'], keep=False)
    last_rows = df[duplicates_mask].groupby('mrn').tail(1).index
    df.loc[last_rows, 'date'] += pd.to_timedelta('1 minute')
    return df


def calculate_time_since_c1(df):
    """
    Calculate the time since the last (C1) date and result for each 'mrn'.
    """
    df['C1_date'] = df.groupby('mrn')['date'].transform('max')
    df['time_since_C1'] = pd.to_datetime(df['date']) - pd.to_datetime(df['C1_date'])
    df['C1_result'] = df.groupby('mrn')['result'].transform('last')
    return df


def get_nhs_features(df):
    """
    Calculate RV1, RV2, D metrics for the NHS AKI algorithm using date masks.
    """
    required_columns = ['mrn', 'date', 'result']
    if not all(column in df.columns for column in required_columns):
        logging.error("DataFrame missing one or more required columns: 'mrn', 'date', 'result'")
        raise ValueError("Input DataFrame does not have the required columns.")

    try:
        df = adjust_duplicate_dates(df)
        df = calculate_time_since_c1(df)
        within_7_days, within_48h, within_8_to_365_days = get_time_masks(df)

        # Calculate metrics based on time masks
        min_result_within_1W = df[within_7_days].groupby('mrn')['result'].min().reset_index(name='RV1')
        df = pd.merge(df, min_result_within_1W, on='mrn', how='left')

        med_results_within_1Y = df[within_8_to_365_days].groupby('mrn')['result'].median().reset_index(name='RV2')
        df = pd.merge(df, med_results_within_1Y, on='mrn', how='left')

        lowest_within_48h = df[within_48h].groupby('mrn')['result'].min().reset_index(name='lowest_48h')
        df = pd.merge(df, lowest_within_48h, on='mrn', how='left')

        df['D'] = df['C1_result'] - df['lowest_48h']

        logging.info("RV1, RV2, D successfully computed from test results")
        return df
    except Exception as e:
        logging.error(f"Problem computing NHS metrics: {e}")
        raise


def get_summary_observations(df):
    """
    Simplifies DataFrame to include only summary observations, removing individual test information.
    
    Args:
        df (pd.DataFrame): DataFrame containing test results and other patient information.
        
    Returns:
        pd.DataFrame: Summary DataFrame with observations summarized by 'mrn', 'age', 'sex', 'C1_result', 'RV1', 'RV2', 'D',
                      and duplicates removed.
                      
    Raises:
        ValueError: If the input DataFrame does not contain all required columns.
    """
    col_subset = ['mrn', 'age', 'sex', 'C1_result', 'RV1', 'RV2', 'D']
    missing_cols = [col for col in col_subset if col not in df.columns]
    
    if missing_cols:
        error_message = f"Input DataFrame is missing required columns: {', '.join(missing_cols)}"
        logging.error(error_message)
        raise ValueError(error_message)

    try:
        summary_rows = df[col_subset].drop_duplicates().reset_index(drop=True)
        logging.info("Summary observations successfully consolidated.")
        return summary_rows
    except Exception as e:
        logging.error(f"Unable to consolidate features ahead of modelling: {e}")
        raise


""" Step 4: Tie all operations together to prepare the data for modelling """

def preprocess_features(df_obj):
    """
    Preprocesses the features of a given DataFrame through a series of steps.
    We assume each process is crucial, and so if any fails we halt the process.
    Args:
        df_obj (pd.DataFrame): The DataFrame to preprocess.
        
    Returns:
        pd.DataFrame: The preprocessed DataFrame ready for modeling.
        
    Raises:
        Exception: Propagates any exceptions raised by the preprocessing steps.
    """
    logging.info("Starting preprocessing of features.")
    try:
        format_col_types(df_obj)
        logging.info("Column types formatted successfully.")
    except Exception as e:
        logging.error(f"Error in formatting column types: {e}")
        raise

    try:
        data = consolidate_tests(df_obj)
        logging.info("Tests consolidated successfully.")
    except Exception as e:
        logging.error(f"Error in consolidating tests: {e}")
        raise

    try:
        data = get_nhs_features(data)
        logging.info("NHS features calculated successfully.")
    except Exception as e:
        logging.error(f"Error in calculating NHS features: {e}")
        raise

    try:
        data = get_summary_observations(data)
        logging.info("Summary observations obtained successfully.")
    except Exception as e:
        logging.error(f"Error in summarizing observations: {e}")
        raise

    logging.info("Preprocessing completed successfully.")
    return data