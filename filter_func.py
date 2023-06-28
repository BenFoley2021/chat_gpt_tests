def filter_df(df):
    """
    Filter a pandas data frame by Views greater than 100_000
    
    Parameters
    ----------
    df : pandas dataframe
        Dataframe to filter
        
    Returns
    -------
    df : pandas dataframe
        Filtered dataframe
    """
    df = df[df['Views'] > 100_000]
    return df