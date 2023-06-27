import pandas as pd

def filter_df(df):
  df = df.loc[(df['Views Growth'] > 0) & (df['Viewing Affinity'] > df['Viewing Affinity'].quantile(0.9))]
  return df