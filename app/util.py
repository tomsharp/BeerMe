import pandas as pd
import sqlite3
import json

with open('config.json') as f:
    config_params = json.load(f)

def beer_options():

    query = "SELECT DISTINCT beer_name FROM user_extract"
    with sqlite3.connect(config_params['DATABASE_PATH']) as conn:
        beers = list(pd.read_sql(query, conn))
    
    beer_options = [{'label': beer, 'value': beer} for beer in list(pd.read_sql(query,conn)['beer_name'])]

    return beer_options