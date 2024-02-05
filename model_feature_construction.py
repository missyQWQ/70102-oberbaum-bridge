import numpy as np
import pandas as pd
"""
Purpose of script: To transform input of the form 

MRN|age|sex|creatinine_date_0|creatinine_result_0|creatinine_date_1|creatinine_result_1
 0 | 18| f |       X         |        a          |       Y         |       b

into what the model requires:
    
MRN|age|sex|C1_result|RV1|RV2|D |
 0 | 18| f |   100.0 | 98|102|33|

"""

def format_date_cols(data):
    """ Finds and formats all date columns into %Y-%m-%d %H:%M:%S"""
    date_cols = data.filter(like='_date_').columns
    for date_col in date_cols:
        data[date_col] = pd.to_datetime(data[date_col], dayfirst=True)


def format_result_cols(data):
    """Coerces all creatinine result features in type float"""
    result_cols = data.filter(like='_result_').columns
    for result_col in result_cols:
        data[result_col] = pd.to_numeric(data[result_col])


def format_other_cols(data):
    """Coerces other column data types to how we would expect"""
    data['age'] = pd.to_numeric(data["age"])
    # We would prefer string cols, not object cols as in Numpy:
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/text.html
    data['sex'] = data['sex'].astype('string')


def format_col_types(data):
    """Wrapper function to call all column type casting/formatting"""
    try:
        format_date_cols(data)
        format_result_cols(data)
        format_other_cols(data)
        print("Columns formatted from raw input")
    except:
        print("Columns could not be formatted")


def read_and_format_data(data_frame_obj):
    """ Read in data frame object from message
    Args:
        data_frame_obj (pd.DataFrame): new message plus old results

    Returns:
        pd.DataFrame: DataFrame with correct column types
    """
    try:     
        # Read in the data
        data_frame_obj['id'] = data_frame_obj.index # used for pivoting data
        print("Data loaded successfully")
        
        # Format the column dtypes
        format_col_types(data_frame_obj)
        return data_frame_obj
    except:
        print("Data load failed")

        
def consolidate_tests(df):
    try:
        """ Takes observation of df and consolidates test dates and scores.
        
        For example, 
        id|creatinine_date_0|creatinine_result_0|creatinine_date_1|creatinine_result_1
         0|        X        |        a          |       Y         |       b
        into:
        id| date | result |
         0|  X   |   a    |
         0|  Y   |   b    | 
        
        Args:
            df (pd.DataFrame): dataframe from which an observation is selected
            
        Returns:
            pd.DataFrame: observation i but with a dates and results column
        """
        id_cols = ['id', 'age', 'sex']
        
        df_long = df.melt(id_vars = id_cols)
        df_long = df_long.dropna(subset=['value'])
        df_long['test'] = df_long['variable'].str.split('_').str[-1]
        df_long['variable'] = df_long['variable'].str.split('_').str[1]
        df_wide = df_long.pivot_table(index = id_cols + ['test'],
                                              columns = 'variable',
                                              values = 'value',
                                              aggfunc='first').reset_index()
        print("Data reshaped")
        return df_wide
    except:
        print("Data reshaping failed")

def get_time_masks(df):
    try:
        """ Returns various bool masks depending on timeframe of observation"""
        within_48h = np.logical_and(
            df['time_since_C1'] > pd.Timedelta(value=-48, unit = 'hours'),
            df['time_since_C1'] < pd.Timedelta(value=0)
            )
        
        within_8_to_365_days = np.logical_and(
            df['time_since_C1'] > pd.Timedelta(value=-366, unit = 'days'),
            df['time_since_C1'] < pd.Timedelta(value=-8, unit = 'days'),
            ) 
        
        within_7_days = np.logical_and(
            df['time_since_C1'] > pd.Timedelta(value=-8, unit = 'days'),
            df['time_since_C1'] < pd.Timedelta(value=0))
        print("Time masks constructed")
        return within_7_days, within_48h, within_8_to_365_days
    except:
        print("Failed to construct time masks")


def get_nhs_features(df):
    """ Calculate RV1, RV2, D metrics for the NHS AKI algorithm:
        
    Reference: https://www.england.nhs.uk/akiprogramme/aki-algorithm/
    
    Uses date masks to separate various results by their time relative to 
    the latest result (C1). Then calculates aggregations based on the subsets.
    
    Args:
        df (pd.DataFrame): columns ['variable', 'id', 'age' ... 'date', 'result']
        
    Returns:
        pd.DataFrame: returns df with columns of RV1, RV2, D added
        
    """
    try:
        # Add arbitrary minute to where we have duplicates of 'id' and 'date'
        # Occassionally we have two tests results within the same minute, e.g. id 328005
        duplicates_mask = df.duplicated(subset=['id', 'date'], keep='first') | df.duplicated(subset=['id', 'date'], keep='last')
        last_rows = df[duplicates_mask].groupby('id').tail(1).index
        df.loc[last_rows, 'date'] = df.loc[duplicates_mask, 'date'] + pd.to_timedelta('1 minute')
        
        df['C1_date'] =  df.groupby('id')['date'].transform('max')
        df['time_since_C1'] = pd.to_datetime(df['date']) - pd.to_datetime(df['C1_date'])
        df['C1_result'] = df.groupby('id')['result'].transform('last')
        
        within_7_days, within_48h, within_8_to_365_days = get_time_masks(df)
        
        # From these reference points, derive the metrics
        min_result_within_1W = df[within_7_days].groupby('id')['result'].min().reset_index()
        min_result_within_1W.rename(columns = {'result': 'RV1'}, inplace = True)
        df = pd.merge(df, min_result_within_1W, on='id', how='left')
        
        med_results_within_1Y = df[within_8_to_365_days].groupby('id')['result'].median().reset_index()
        med_results_within_1Y.rename(columns = {'result': 'RV2'}, inplace = True)
        df = pd.merge(df, med_results_within_1Y, on='id', how='left')
        
        lowest_within_48h = df[within_48h].groupby('id')['result'].min().reset_index()
        lowest_within_48h.rename(columns = {'result': 'lowest_48h'}, inplace = True)
        df = pd.merge(df, lowest_within_48h, on='id', how='left')
        df['D'] = df['C1_result'] - df['lowest_48h']
        print("RV1, RV2, D successfully computed from test results")
        return df
    except:
        print("Problem computing NHS metrics")


def get_summary_observations(df):
    try:
        """ Simple function to remove individual test information now captured """
        col_subset = ['age', 'sex', 'C1_result', 'RV1', 'RV2', 'D']
        """ Return an observation with all test results summarised by CV, RV1, RV2, D """
        summary_rows = df[col_subset]
        summary_rows = summary_rows.drop_duplicates()
        summary_rows.reset_index(drop=True, inplace=True)
        print("Data ready to model on")
        return summary_rows
    except:
        print("Unable to consolidate features ahead of modelling")


def preprocess_features(df_obj):
    data = read_and_format_data(df_obj)
    data = consolidate_tests(data)
    data = get_nhs_features(data)
    data = get_summary_observations(data)
    return data

    
