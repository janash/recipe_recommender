"""
Functions to scrape and clean recipes from bodybuilding.com database
"""

import os

import bs4
import pandas as pd
import requests
import json


def scrape_db():
    """
    Function to scrape bodybuild.com recipe database and save results as json.
    """

    # Hacky way to get all recipes - you have to request the number. Luckily,
    # this is listed at the beginning of any result you pull from DB.
    # We want all of the recipes, so we'll do a quick request of one recipe to
    # get the 'total' number in the DB
    url_request = 'https://cms-api.bodybuilding.com/BbcomRecipe'
    url_parameters = {'sort':'publishDate', 'order': 'desc', 'limit':'1'}

    fake_recipes_list = requests.get(url_request, params=url_parameters)
    fake_recipes = bs4.BeautifulSoup(fake_recipes_list.content, features='html.parser')
    fake = json.loads(str(fake_recipes))

    # Get the total number of recipes in the db
    total_recipes = fake['total']

    # Change the 'limit' on the url to the total number of recipes
    url_parameters = {'sort':'publishDate', 'order': 'desc', 'limit': str(total_recipes)}

    all_recipes_list = requests.get(url_request, params=url_parameters)
    all_recipes = bs4.BeautifulSoup(all_recipes_list.content, features='html.parser')

    # Just get search results and get rid of data before.
    all_recipes_list = json.loads(str(all_recipes))['_embedded']['bb-cms:search-results']

    # Dump to json file - results will always be saved in 'data' folder
    save_path = os.path.join('..','data', 'bodybuilding_recipes.json')
    rf = open(save_path, 'w')
    json.dump(all_recipes_list, rf)
    rf.close()

def save_df():
    """
    Create pandas dataframe from json and save as csv
    """

    # Define file name
    base_path = os.path.join('..', 'data')
    open_path = os.path.join(base_path, 'bodybuilding_recipes.json')
    save_path = os.path.join(base_path, 'bodybuilding_recipes.csv')

    # Check that file exists - if not use scrape_db function
    if not os.path.isfile(open_path):
        scrape_db()

    # Load from json
    with open(open_path) as f:
        data = json.load(f)

    # Now we need to "flatten" this data. Nutrituin information is nested.
    recipe_0 = data[0]
    keys_of_interest = list(recipe_0['schemaOrg'].keys())[2:]

    # Create empty dict
    data_holder = {}

    # Determine structure from first recipe
    for key in keys_of_interest:
        if isinstance(recipe_0['schemaOrg'][key], dict):
            for deep_key in recipe_0['schemaOrg'][key].keys():
                if '@' not in deep_key:
                    data_holder[deep_key] = []
        else:
            data_holder[key] = []

    # Fill in dictionary
    for recipe in data:
        for key in keys_of_interest:
            if key in recipe['schemaOrg'].keys():
                if isinstance(recipe['schemaOrg'][key], dict):
                    for deep_key in recipe['schemaOrg'][key].keys():
                        if '@' not in deep_key and deep_key != 'name':
                            data_holder[deep_key].append(recipe['schemaOrg'][key][deep_key])
                else:
                    data_holder[key].append(recipe['schemaOrg'][key])

    # Create dataframe
    df = pd.DataFrame.from_dict(data_holder)

    # Save as csv
    df.to_csv(save_path)
