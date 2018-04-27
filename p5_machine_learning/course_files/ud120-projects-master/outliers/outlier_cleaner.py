#!/usr/bin/python


def outlierCleaner(predictions, ages, net_worths):
    """
        Clean away the 10% of points that have the largest
        residual errors (difference between the prediction
        and the actual net worth).

        Return a list of tuples named cleaned_data where 
        each tuple is of the form (age, net_worth, error).
    """
    
    ### your code goes here

    import pandas as pd

    # Setting up dataframe
    df = pd.DataFrame(predictions, columns=['pred'])
    df['age'] = ages
    df['net_worth'] = net_worths
    df['error'] = abs(df['net_worth'] - df['pred'])
    
    # Defining which data points to remove
    df['remove'] = df['error'] >= df['error'].quantile(0.9)
    # Dataframe for output
    df_cleaned_data = df[df['remove'] == False][['age', 'net_worth', 'error']]
    # List of tuples output
    cleaned_data = list(df_cleaned_data.itertuples(index=False, name=None))
    
    return cleaned_data

