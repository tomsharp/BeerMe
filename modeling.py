# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 21:25:32 2019

@author: tomsharp
"""

from BeerMe.Pipeline import *

df = IMPORT_CLEAN_STEP(db_path='data/beer.db')
df = COSINE_STEP(df)

features = ['ABV', 'IBU', 'global_rating']
target = ['user_rating']
df, X_scaler, y_scaler = transform_features_target(df, features, target) 


cols = ['username', 'nearest_neighbor_rank'] + features + target
df = df[cols]



##################
l1_ratio_space = [.1, .5, .7, .9, .95, .99, 1]
min_ppu_list = [0, 50, 100, 250, 500, 750, 1000]
n_users_list = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 
                55, 60, 65, 70, 75, 80, 85, 100, len(df['username'].unique())-1]


mae_list = []
quarter_abs_error_list = []
half_abs_error_list = []
    

for min_ppu in min_ppu_list:
    
    print(min_ppu)
    
    user_indices = df.username.value_counts()[df.username.value_counts() > min_ppu].index
    sub_df = df[df['username'].isin(user_indices)]
    n_users_list = [n_users for n_users in n_users_list if n_users < len(user_indices)]

    for top_n in n_users_list:
        
        # split data 
        top_n_nn = list(sub_df['nearest_neighbor_rank'].unique())[:top_n]
        df_top_n = df[df['nearest_neighbor_rank'].isin(top_n_nn)]
        X_train = df_top_n[features]
        y_train = df_top_n[target]

        X_test = df[df['username'] == user_of_reference][features]
        y_test = df[df['username'] == user_of_reference][target]

        # train
        from sklearn.linear_model import ElasticNetCV
        model = ElasticNetCV(fit_intercept=False, normalize=False, l1_ratio=l1_ratio_space, cv=5, random_state=rand_state)
        model.fit(X_train, y_train)

        # Evaluate model on user's data 
        preds = model.predict(X_test)

        # unscale
        preds_unscaled = y_scaler.inverse_transform(preds)
        y_test_unscaled = y_scaler.inverse_transform(y_test)

        # evaluate results
        results_df = pd.DataFrame([preds_unscaled, y_test_unscaled]).transpose()
        results_df.columns = ['predicted', 'actual']
        results_df['error'] = results_df['predicted'] - results_df['actual']
        results_df['abs_error'] = abs(results_df['error'])

        # Performance Metrics 
        mae = np.mean(results_df['abs_error'])

        quarter_abs_error_list.append(100*len(results_df[results_df['abs_error']<=0.25])/len(results_df))
        half_abs_error_list.append(100*len(results_df[results_df['abs_error']<=0.50])/len(results_df))
        mae_list.append(mae)

        print('MAE =', np.round(mae,5), 
              'with % within 0.25', 100*len(results_df[results_df['abs_error']<=0.25])/len(results_df), 
              'and % within 0.5', 100*len(results_df[results_df['abs_error']<=0.50])/len(results_df),
              "for n =", top_n, "with alpha =", np.round(model.alpha_, 5), "and l1 ratio = ", model.l1_ratio_)
    
    # add breaks
    quarter_abs_error_list.append(0)
    half_abs_error_list.append(0)
    mae_list.append(0)