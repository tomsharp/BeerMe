# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

def BreweryDB_request(uri, endpoint, options={}, api_key=""):
    if api_key == "":
        raise ValueError("Please pass in an API key")
    else:
        import requests
        url = uri + '/' + endpoint + '/' 
        options['key'] = api_key
        response = requests.get(url, options)
        return response


def login_untappd(untappd_username, untappd_password, driver):
    # login
    print("logging into Untappd...")
    login_url = 'https://untappd.com/login'
    driver.get(login_url)
    driver.find_element_by_id("username").send_keys(untappd_username)
    driver.find_element_by_id("password").send_keys(untappd_password)
    driver.find_element_by_xpath("/html/body/div/div/div/form/span/input").click()

def get_beer_history(username, driver):
    import pandas as pd
    import math
    import time
    
    # navigate
    print("navigating to user's profile...")
    url = 'https://untappd.com/user/' + username + '/beers'
    driver.get(url)
    
    # get number of beers
    n_beers_element = driver.find_element_by_xpath("""//*[@id="slide"]/div[2]/div/div[2]/div[1]/div/div[2]/a[2]/span[1]""")
    n_beers = int(n_beers_element.get_attribute("innerHTML").replace(',', ''))
    clicks_needed = math.ceil(n_beers/25) - 1
    
    # close app download banner
    try:
        time.sleep(2)
        iframe = driver.find_element_by_id("branch-banner-iframe")
        driver.switch_to.frame(iframe)
        driver.find_element_by_id("branch-banner-close").click()
    except:
        pass
    
    # expand page to show all beers 
    print("retrieving beers...")
    clicks_made = 0
    while clicks_made < clicks_needed:
        print("executing click number " + str(clicks_made+1) + " of " + str(clicks_needed))
        try:
            driver.find_element_by_class_name("more-list-items").click()
            clicks_made += 1
        except:
            time.sleep(1.5)
    
    # gather beers
    beers = driver.find_elements_by_class_name("beer-item")
    print("retrieved all beers")
   
    # clean and consolidate data into df   
    print("building dataframe...")
    beer_list = []
    for beer in beers:
        #split 
        attribute_list = beer.text.split('\n')
        
        # clean
        user_attr = [attr for attr in attribute_list if attr.find("THEIR") == 0]
        if user_attr != []:
            user_rating = float(user_attr[0].split('(')[1].split(')')[0])
        else:
            user_rating = None
        
        global_attr = [attr for attr in attribute_list if attr.find("GLOBAL") == 0]
        if global_attr != []:
            global_rating = float(global_attr[0].split('(')[1].split(')')[0])
        else:
            global_rating = None
        
        # parse last index in attribute_list
        tail = attribute_list[-1]
        try:
            abv = float(tail.split('% ABV')[0])
        except:
            if tail.split(' ABV')[0] == 'No':
                abv = None
        ibu = tail.split('ABV ')[1].split(' IBU')[0]
        if ibu == 'No':
            ibu = None
        first =  tail.split('First: ')[1].split(" Recent")[0]
        recent = tail.split("Recent: ")[1].split(" Total")[0]
        total = int(tail.split("Total: ")[1])
        
        # zip
        attribute_list = attribute_list[:3] + [user_rating, global_rating, abv, ibu, first, recent, total]
        names = ['beer_name', 'brewery', 'beer_description', 'user_rating', 
                 'global_rating', 'ABV', 'IBU', 
                 'first_date', 'recent_date', 'total']
        beer_dict = dict(zip(names, attribute_list))
        
        # append to collection of beer_dicts
        beer_list.append(beer_dict)
    
    beer_df = pd.DataFrame(beer_list)
    beer_df['username'] = username
    beer_df = beer_df[['username', 'beer_name', 'beer_description', 'brewery',
                       'ABV', 'IBU', 'global_rating', 'user_rating',
                       'first_date', 'recent_date', 'total']]

    print("dataframe complete. enjoy your beer!")
    return beer_df

def find_next_friend(username, driver):
    import numpy as np
    
    # navigate
    print("finding a drinking buddy...")
    url = 'https://untappd.com/user/' + username + '/friends'
    driver.get(url)
    
    # pick random friend
    friends = driver.find_elements_by_class_name("friend-item")
    n_friends = len(friends)
    rand_num = np.random.randint(0, n_friends)
    friend = friends[rand_num].text.split('\n')[1]
    
    print(str(friend) + " is your new drinking buddy!")
    return friend

def beer_df2db(beer_df, db_path, table_name='user_extract'):
    # connect to db and write to db
    print("saving your beer for later...")
    import sqlite3
    with sqlite3.connect(db_path) as conn:
        beer_df.to_sql(table_name, conn, if_exists='append', index=False)
    print("beer succesfully saved! (db path = " + db_path + ")")

def random_walk(n_users, starting_username, driver, db_path):
    username = starting_username
    users_scraped = 0
    while users_scraped < n_users:
        beer_df = get_beer_history(username, driver)
        beer_df2db(beer_df, db_path)
        users_scraped += 1
        print(users_scraped)
        username = find_next_friend(username, driver)
        