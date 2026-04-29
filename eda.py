import pandas as pd

df = pd.read_csv('data/raw/churn.csv')

print("Shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nMissing values:\n", df.isnull().sum())
print("\nDuplicates:", df.duplicated().sum())
print("\nData types:\n", df.dtypes)
print("\nBasic stats:\n", df.describe())


df_dirty = df.copy()
df_dirty.loc[0:5000, 'Age'] = None          
df_dirty.loc[5000:8000, 'Total Spend'] = -999 
df_dirty.loc[8000:10000, 'Support Calls'] = 99
df_dirty = pd.concat([df_dirty, df_dirty.iloc[:6000]])  

df_dirty.to_csv('data/raw/churn_dirty.csv', index=False)
print("Dirty dataset created: 500 nulls, 100 invalid values, 200 duplicates")