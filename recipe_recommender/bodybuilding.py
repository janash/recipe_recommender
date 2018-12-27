"""
Functions to scrape and clean recipes from bodybuilding.com database
"""

import os

import bs4
import pandas as pd
import requests
import json

# Define file names
_base_path = os.path.join('..', 'data')
_open_path = os.path.join(_base_path, 'bodybuilding_recipes.json')
_save_path = os.path.join(_base_path, 'bodybuilding_recipes.pkl')

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

    # Check that data directory exists, if not, create it
    if not os.path.isdir(_base_path):
        os.mkdir(_base_path)

    # Check that file exists - if not use scrape_db function
    if not os.path.isfile(_open_path):
        scrape_db()

    # Load from json
    with open(_open_path) as f:
        data = json.load(f)

    # Now we need to "flatten" this data. Nutrituin information is nested.
    recipe_0 = data[0]
    keys_of_interest = list(recipe_0['schemaOrg'].keys())[2:]

    # Create empty dict
    data_holder = {}

    # Determine structure from first recipe
    for key in keys_of_interest:
        print(key)
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

    # Save as pickle
    df.to_pickle(_save_path)

def process_nutrition():
    """
    Takes nutrition information from json and saves as csv (for later procesing)

    Parameters:
    --------------------
    data: dict
        json from bodybuilding.com
    """

    with open(_open_path) as f:
        data = json.load(f)

    nutrition_dict = {}
    unit_dict = {}
    recipe_ids = []

    # Build empty dict and get units
    for key in data[0]['schemaOrg']['nutrition'].keys():
        if '@' not in key:
            split_cell = data[0]['schemaOrg']['nutrition'][key].split(' ')
            unit = None
            if len(split_cell)>1:
                unit = split_cell[1]
            nutrition_dict[key] = []
            unit_dict[key] = unit

    # Loop through recipes
    for recipe in data:
        # Only store if recipe has nutritin info
        if 'nutrition' in recipe['schemaOrg'].keys():
            recipe_ids.append(recipe['id'])
            for key in nutrition_dict.keys():
                value = recipe['schemaOrg']['nutrition'][key]
                split_value = value.split(' ')
                if len(split_value) == 2 and key != 'servingSize':
                    nutrition_dict[key].append(split_value[0])
                else:
                    print(key, value)
                    nutrition_dict[key].append(value)

    nutrition_dict['id'] = recipe_ids

    # Modify so that units are in nutrition dict keys
    for key, value in unit_dict.items():
        if value:
            new_key = key + ' (' + value + ')'
            nutrition_dict[new_key] = nutrition_dict.pop(key)

    # Create dataframe
    df = pd.DataFrame.from_dict(nutrition_dict)

    save_path = os.path.join(_base_path, 'bodybuilding_nutrition.csv')
    df.to_csv(save_path, index=False)
