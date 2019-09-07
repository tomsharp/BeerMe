#!/usr/bin/env python
# coding: utf-8

# # Pipeline


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from sklearn.preprocessing import StandardScaler
from functools import reduce

def pipeline_func(data, fns):
    return reduce(lambda a, x: x(a), fns, data)


#############################################   
# 1. Import, Clean, EDA
#############################################     

# @TODO - rename this function
def import_table(db_path, 
                 query = "SELECT * FROM user_extract",
                 remove_dups=True):
    
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(query, conn)
    
    if remove_dups==True:
        df = df[~df.duplicated()]
    
    return(df)
    
def convert_categorical(df, 
                        categorical_variables = ['beer_description', 'brewery']):
    # b. one-hot encode categorical variables
    for cat_var in categorical_variables:
        dummies = pd.get_dummies(df[cat_var], drop_first=True, prefix=cat_var)
        df = pd.merge(df, dummies, left_index=True, right_index=True)
        
    return(df)
    

def outlier_analysis(df, features = ['ABV', 'global_rating', 'user_rating', 'IBU']):
    # c. flag outliers
    print('\n')
    print("1. NA Count...")
    print(df.loc[:,features].isna().sum())
    
    print('\n')
    print('2. Finding IQR outliers...')
    for feature in features:
        df[feature] = df[feature].astype(float)
        try:
            q1 = df[feature].quantile(.25)
            q3 = df[feature].quantile(.75)
            iqr = q3 - q1
            non_outlier_mask = (df[feature] >= q1 - 1.5*iqr) & (df[feature] <= q3 + 1.5*iqr)
            outliers = df[~non_outlier_mask]
    
            print("FEATURE {}".format(feature))
            print("num of outliers = {:,d}".format(len(outliers)))
            print("% of outliers = {:.2f}%".format(100*len(outliers)/len(df)))
            print("\n")
            
        except TypeError:
            print("FEATURE {}".format(feature))
            print("ANALYZING ALL NON-NA VALUES")
            
            non_nas = df[~df[feature].isna()][feature].astype(float)
            q1 = non_nas.quantile(.25)
            q3 = non_nas.quantile(.75)
            iqr = q3 - q1
            non_outlier_mask = (non_nas >= q1 - 1.5*iqr) & (non_nas <= q3 + 1.5*iqr)
            outliers = non_nas[~non_outlier_mask]
            print("num of outliers = {:,d}".format(len(outliers)))
            print("% of outliers = {:.2f}%".format(100*len(outliers)/len(non_nas)))
    
        #    print("\n")
        #    print("4. Plotting feature...")
        #    for feature in features:    
        #        try:
        ##            plt.boxplot(df[feature])
        ##            plt.title(feature)
        ##            plt.show()
        #            df[feature].hist()
        #        except:
        #            pass
        
        return df

def remove_outliers(df, features):
    for feature in features:
        df[feature] = df[feature].astype(float)
        q1 = df[feature].quantile(.25)
        q3 = df[feature].quantile(.75)
        iqr = q3 - q1
        non_outlier_mask = (df[feature] >= q1 - 1.5*iqr) & (df[feature] <= q3 + 1.5*iqr)
        df = df[non_outlier_mask]

    return df


def impute_na(df, features = ['ABV', 'global_rating', 'user_rating', 'IBU'],
              impute_method = 'mean'):

    for feature in features:
        if impute_method == 'mean':
            non_nas = df[~df[feature].isna()][feature].astype(float)
            feature_mean = non_nas.mean()
            df[feature] = df[feature].fillna(feature_mean)
        elif impute_method == 0:
            non_nas = df[~df[feature].isna()][feature].astype(float)
            df[feature] = df[feature].fillna(0)
    
    print("NA Count...")
    print(df.loc[:,features].isna().sum())
    
    return df
    

def IMPORT_CLEAN_STEP(db_path = '../data/beer.db', remove_outliers=False):
    df = import_table(db_path)
    if remove_outliers == False:
        df = pipeline_func(df, [convert_categorical, outlier_analysis, impute_na])
    elif remove_outliers == True:
        df = pipeline_func(df, [convert_categorical, outlier_analysis, remove_outliers, impute_na])
    return df


######################################################     
### 2. Cosine Similarity / Nearest Neighbors
######################################################     
def create_ui_matrix(df, fill_method=0):
    # Create User-Item Matrix 
    data = df
    values = 'user_rating'
    index = 'username'
    columns = 'beer_name'
    agg_func = 'mean'
    
    if fill_method == 'item_mean':
        ui_matrix = pd.pivot_table(data=data, values=values, index=index, 
                                   columns=columns, aggfunc=agg_func)
        ui_matrix = ui_matrix.fillna(ui_matrix.mean(axis=0), axis=0)
    
    elif fill_method == 'user_mean':
        ui_matrix = pd.pivot_table(data=data, values=values, index=index, 
                                   columns=columns, aggfunc=agg_func)
        ui_matrix.apply(lambda row: row.fillna(row.mean()), axis=1)
    
    elif fill_method == 0:
        ui_matrix = pd.pivot_table(data=data, values=values, index=index, 
                                   columns=columns, aggfunc=agg_func, fill_value=0)
    else:
        raise ValueError("Please checkout 'fill_method' value")
    
    ui_matrix.columns = list(ui_matrix.columns)
    
    return(ui_matrix)


# c. Calculate Cosine Similarity
def calculate_cosine_similarity(user_of_reference, ui_matrix):

    # Calculate Cosine Similarity 
    print("User of Reference for Cosine Sim = {}".format(user_of_reference))
    
    from sklearn.metrics.pairwise import cosine_similarity
    X = ui_matrix[ui_matrix.index == user_of_reference]
    Y = ui_matrix[ui_matrix.index != user_of_reference]
    
    sim = cosine_similarity(X,Y)[0].tolist()
    names = Y.index
    
    sim_df = pd.DataFrame({'username':names, 'sim_score':sim})
    sim_df = sim_df.sort_values(by='sim_score', ascending=False)
    
    return(sim_df)


def calculate_nearest_neighbors(sim_df):
    # add neighbor rank to df
    neighbor_rank = sim_df.reset_index(drop=True)
    neighbor_rank.index.name = 'nearest_neighbor_rank'
    neighbor_rank.reset_index(inplace=True)
    neighbor_rank['nearest_neighbor_rank'] = neighbor_rank['nearest_neighbor_rank'] + 1
    neighbor_rank = neighbor_rank[['nearest_neighbor_rank', 'username']]
    return(neighbor_rank)

def merge_nearest_neighobr_rank(df, neighbor_rank):    
    df = pd.merge(neighbor_rank, df, on='username', how='outer')
    
    return(df)


def COSINE_STEP(df, user_of_reference):
    ui_matrix = create_ui_matrix(df)
    sim_df = calculate_cosine_similarity(user_of_reference, ui_matrix)
    neighbor_rank = calculate_nearest_neighbors(sim_df)
    df = merge_nearest_neighobr_rank(df, neighbor_rank)
    return df
    
######################################################   
### 3. Scale / Standardize Data 
######################################################   
def transform_features_target(df, features, target):
    X_scaler = StandardScaler()
    X_scaler.fit(df[features])
    df[features] = X_scaler.transform(df[features])
    
    y_scaler = StandardScaler()
    y = np.array(df[target]).reshape(-1, 1 )
    y_scaler.fit(y)
    df[target] = y_scaler.transform(y)
    
    feature_scaler = X_scaler
    target_scaler = y_scaler 
    
    return(df, feature_scaler, target_scaler)