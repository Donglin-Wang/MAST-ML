"""
Module for loading checking the input data file
"""

import pandas as pd
import logging

log = logging.getLogger('mastml')


def load_data(
              file_path,
              input_features=None,
              target_feature=None,
              grouping_feature=None,
              feature_blacklist=list()
              ):

    '''
    Loads in csv from filename and ensures required columns are present.
    Returns dataframe.
    '''

    # Load data
    try:
        df = pd.read_csv(file_path)
    except Exception:
        df = pd.read_excel(file_path)

    # Assign default values to input_features and target_feature;
    # input is first n-1 and target is just n
    if input_features is None and target_feature is None:
        input_features = list(df.columns[:-1])
        target_feature = df.columns[-1]

    # input is all the features except the target feature
    elif input_features is None:
        input_features = [col for col in df.columns if col != target_feature]

    # target is the last non-input feature
    elif target_feature is None:
        for col in df.columns[::-1]:
            if col not in input_features:
                target_feature = col
                break

    # Collect required features:
    required_features = input_features + [target_feature]

    # Ensure they are all present:
    for feature in required_features:
        if feature not in df.columns:
            raise Exception(f"Data file does not have column '{feature}'")

    X, y = df[input_features], df[target_feature]

    log.info(
             'blacklisted features, either from ' +
             '"not_input_features" or a "grouping_column":' +
             str(feature_blacklist)
             )

    # take blacklisted features out of X:
    X_noinput_dict = dict()
    for feature in set(feature_blacklist):
        X_noinput_dict[feature] = X[feature]
        X = X.drop(feature, axis=1)

    X_noinput = pd.DataFrame(X_noinput_dict)

    if grouping_feature:
        X_grouped = pd.DataFrame(df[grouping_feature])

    else:
        X_grouped = None

    df = df.drop(target_feature, axis=1)

    return df, X, X_noinput, X_grouped, y
