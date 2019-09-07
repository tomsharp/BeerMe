from data_pipeline import *

# import data
print("IMPORTING DATA FROM 'user_extract' TABLE")
df = import_table(db_path)

# drop unnecessary columns
print("DROPPING UNECESSARY COLS")
df = df[['username', 'beer_name', 'beer_description', 'brewery', 'ABV', 'IBU', 'global_rating', 'user_rating']]

# impute na w/ mean
cols = ['ABV', 'IBU', 'global_rating', 'user_rating']
na_method = 'mean' 
print("IMPUTING NA of {} with {}".format(cols, na_method))
df = impute_na(df, features=cols, impute_method=na_method)

# convert datatype
print("CONVERTING DATATYPE OF IBU TO FLOAT")
df['IBU'] = df['IBU'].astype(float)

# perform outlier analysis and removal if necessary
print("PERFORMING OUTLIER ANALYSIS")
features = ['ABV', 'IBU', 'global_rating', 'user_rating']
df = outlier_analysis(df, features)

# dump prepared data to 'prepped_data' table
print("WRITING PREPARED DATA TO 'prepped_data' TABLE")
conn = sqlite3.connect(db_path)
df.to_sql('prepped_data', conn, if_exists='replace', index=False)