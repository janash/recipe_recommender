"""
Functions to scrape and clean recipes from bodybuilding.com database
"""

import os
import urllib

import bs4
import pandas as pd
import requests
import json

from pathlib import Path

__all__ = ["scrape_db", "save_df", "process_nutrition", "process_instructions",
            "process_ingredients"]

# Define file names
_current_dir = Path(__file__).parent

_DATA_DIR = _current_dir.joinpath(_current_dir, '..', '..', 'data')
_CLEANED_DATA_DIR = _DATA_DIR.joinpath('cleaned')

_open_path = Path.joinpath(_DATA_DIR, 'bodybuilding_recipes.json')
_save_path = Path.joinpath(_DATA_DIR, 'bodybuilding_recipes.pkl')

def scrape_db(test=False, write_file=True):
    """
    Function to scrape bodybuild.com recipe database and save results as json.

    Parameters:
    -----------

    """

    # Hacky way to get all recipes - you have to request the number. Luckily,
    # this is listed at the beginning of any result you pull from DB.
    # We want all of the recipes, so we'll do a quick request of one recipe to
    # get the 'total' number in the DB
    url_request = 'https://cms-api.bodybuilding.com/BbcomRecipe'
    url_parameters = {'sort': 'publishDate', 'order': 'desc', 'limit': '1'}

    fake_recipes_list = requests.get(url_request, params=url_parameters)
    fake_recipes = bs4.BeautifulSoup(fake_recipes_list.content, features='html.parser')
    fake = json.loads(str(fake_recipes))

    # Get the total number of recipes in the db
    total_recipes = fake['total']

    if test == True:
        all_recipes = fake_recipes

    else:
        # Change the 'limit' on the url to the total number of recipes
        url_parameters['limit'] = str(total_recipes)

        all_recipes_list = requests.get(url_request, params=url_parameters)
        all_recipes = bs4.BeautifulSoup(all_recipes_list.content, features='html.parser')

    # Just get search results and get rid of data before.
    all_recipes_list = json.loads(str(all_recipes))['_embedded']['bb-cms:search-results']

    # Dump to json file - results will always be saved in 'data' folder
    if write_file:
        save_path = _DATA_DIR.joinpath('bodybuilding_recipes.json')
        rf = open(save_path, 'w')
        json.dump(all_recipes_list, rf)
        rf.close()

    return all_recipes_list

def get_extra_data(recipe_list, write_file=True, filename='bodybuilding_recipes_all_info.json'):
    """
    Get extra data with each recipe. Some tags (such as 'breakfast', 'dessert' are not included with the initial query.)
    
    This function takes the json from the scrape_db function, and visits each recipe page on the website in order to
    get extra tags associated with the recipe.

    Parameters
    ----------
    recipe_list : dict
        Recipes obtained from querying bodybuilding.com with scrape_db function.
    write_file: bool (optional)
        Write scraped data to file.
    """
    new_data = []
    bad_slugs = []

    # This try/except is for in case of any errors. There is currently one. Some recipe is misspelled on the slug.
    for recipe in recipe_list:
        slug = recipe['slug']
        try:
            contents = urllib.request.urlopen('https://www.bodybuilding.com/recipes/'+slug).read()
            soup = bs4.BeautifulSoup(contents, features='html.parser')
            scripts = soup.find_all('script', type="application/ld+json")
            json_recipe = json.loads(scripts[0].text)
            new_data.append(json_recipe)
        except:
            bad_slugs.append(slug)
    
    if write_file:
        save_path = _DATA_DIR.joinpath(filename)
        rf = open(save_path, 'w')
        json.dump(new_data, rf)
        rf.close()

    return new_data, bad_slugs

def flatten_json(json_data, current_key=None, current_dict=None):
    """
    Flatten a nested json into a Python dictionary using a recursive strategy 

    Parameters
    ----------
    json_data: json
        Data to process
    """

    if current_dict is None:
        current_dict = {}
    
    if current_key is None:
        current_key= ''

    for k,v in json_data.items():
        current_key += k
        try:
            for k2, v2 in v.items():
                flatten_json(v, current_key=current_key, current_dict=current_dict)
        except:
            current_dict[current_key] = str(v)
            current_key = ''
    
    return current_dict


def save_df():
    """
    Create pandas dataframe from json and save as csv
    """

    # Check that data directory exists, if not, create it
    if not Path.is_dir(_DATA_DIR):
        Path.mkdir(_DATA_DIR)

    # Check that file exists - if not use scrape_db function
    if not Path.exists(_open_path):
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


def process_nutrition(data):
    """
    Takes nutrition information from json and saves as csv (for later procesing)

    Parameters:
    -----------
    data: dict
        json from bodybuilding.com
    """

    nutrition_dict = {}
    unit_dict = {}
    recipe_ids = []

    # Build empty dict and get units
    for key in data[0]['schemaOrg']['nutrition'].keys():
        if '@' not in key:
            split_cell = data[0]['schemaOrg']['nutrition'][key].split(' ')
            unit = None
            if len(split_cell) > 1:
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
                    nutrition_dict[key].append(value)

    nutrition_dict['recipe_id'] = recipe_ids

    # Modify so that units are in nutrition dict keys
    # We actually don't need this :(
    """
    for key, value in unit_dict.items():
        if value:
            new_key = key + ' (' + value + ')'
            nutrition_dict[new_key] = nutrition_dict.pop(key)
    """

    # Create dataframe
    df = pd.DataFrame.from_dict(nutrition_dict)

    save_path = _CLEANED_DATA_DIR.joinpath('recipe_nutrition.csv')
    df.to_csv(save_path, index=False)

def process_instructions(data):
    """
    Takes recipe instructions from json and saves as csv.

    Recipe instructions include information on prep time, cook time (in minutes),
    and instructions (saved as string).

    Note: saving as a csv converts the instructions (stored as list) to string.
    Need to figure out something for this.
    """

    instruction_dict = {
        'id':[],
        'prepTime': [],
        'cookTime': [],
        'totalTime': [],
        'directions': [],
    }

    for recipe in data:
        for key in instruction_dict.keys():
            instruction_dict[key].append(recipe[key])

    save_path = _CLEANED_DATA_DIR.joinpath('recipe_directions.csv')
    instruction_dict['recipe_id'] = instruction_dict.pop('id')
    # Create dataframe
    df = pd.DataFrame.from_dict(instruction_dict)
    df.to_csv(save_path, index=False)

def process_recipe_table(data):
    """
    Takes recipe ids, names, and descriptions from json and saves to table
    """

    instruction_dict = {
        'id': [],
        'description': [],
        'name': []
    }

    for recipe in data:
        for key in instruction_dict.keys():
            instruction_dict[key].append(recipe[key])

    save_path = _CLEANED_DATA_DIR.joinpath('recipes.csv')
    instruction_dict['recipe_id'] = instruction_dict.pop('id')
    instruction_dict['recipe_name'] = instruction_dict.pop('name')

    # Create dataframe
    df = pd.DataFrame.from_dict(instruction_dict)
    df.to_csv(save_path, index=False)

def process_ingredients(data):
    """
    Process the ingredients from bodybuilding.com and save the recipe.
    Each of the ingredients is in formats like shown below:

    white cheddar - 2 oz (ingredient - amount unit)
    green onion, chopped - ¼ cup  (ingredient, descriptor - amount unit)
    salt and pepper to taste (ingredient)

    We will be splitting up the ingredient, amounts, units, and descriptors from these strings.
    For the 3rd case above. The amount will be returned as 0 with units of None.

    This creates the csvs `recipe_ingredients` which has recipe_id, ingredient_id, amount, unit, and descriptor and
    `ingredients` which matches ingredients to ingredient_ids

    # TODO: Some thins are still slipping through. Like this 'banana -  medium (7" to 7-7/8" long)'. Actually right now I think that's the only one it's failing on.

    Parameters
    ---------------------
    data:
        Scraped json from bodybuilding.com
    """

    all_ingredients = []
    all_amounts = []
    all_descriptors = []
    all_units = []
    recipe_ids = []

    for dat in data:
        recipe_id = dat['id']
        dat = dat['schemaOrg']
        if 'recipeIngredient' in dat.keys():
            ingredients = dat['recipeIngredient']
            for ingredient in ingredients:
                descriptor = None  # most recipes will have no descriptors, but we need a placeholder
                amount = None
                unit = None

                recipe_ids.append(recipe_id)

                # replace characters that we can't convert to floats. There has to be a better way
                ingredient = ingredient.replace(u"½", u".5")
                ingredient = ingredient.replace(u"¼", u".25")
                ingredient = ingredient.replace(u"¾", u".75")
                ingredient = ingredient.replace(u"⅛", u".125")
                ingredient = ingredient.replace(u"⅓", u".333")
                ingredient = ingredient.replace(u"1⅓", u"1.333")
                ingredient = ingredient.replace(u"⅔", u".66")
                ingredient = ingredient.replace(u"⅜", u".375")
                ingredient = ingredient.replace(u"⅝", u".625")
                ingredient = ingredient.replace(u"⅞", u".875")
                ingredient = ingredient.replace(u"1⅞", u".875")

                # split ingredient name from amount/unit
                split_ingredients = ingredient.split(' -')
                # now we have something like this ['grilled chicken thighs', ' 5 lb']

                this_ingredient = split_ingredients[0].strip()

                # This should split the amount and unit (eg ['5', 'lb'])
                split_again = split_ingredients[1].strip().split(' ')

                if len(split_again) == 2:
                    amount = split_again[0]
                    unit = split_again[1]

                    # convert the amount to a float
                    try:
                        amount = float(amount)
                    except ValueError:  # this happens with something like `granulated Stevia -  to taste`
                        amount = 0
                        unit = None

                # This is what happens if there are no units (e.g. ingredient is 'avocado - 1' or 'salt and pepper to taste')
                else:
                    try:
                        amount = float(split_again[0])
                        unit = None
                    except ValueError:  # this means it's the second kind in example above
                        amount = 0
                        unit = None

                # Separate out if the ingredient has something like 'spinach, chopped'
                with_descriptors = this_ingredient.split(',')
                if len(with_descriptors) > 1:  # This means there is a description

                    this_ingredient = with_descriptors[0]

                    with_descriptors = with_descriptors[1:]

                    descriptor = ' '.join(with_descriptors).strip().lower()


                else:
                    descriptor = None

                all_ingredients.append(this_ingredient.lower())
                all_amounts.append(amount)
                all_units.append(unit)
                all_descriptors.append(descriptor)

    ingredient_set = sorted(list(set(all_ingredients)))
    ingredient_table = pd.DataFrame({'ingredient': ingredient_set}).reset_index()

    recipe_ingredient_table = pd.DataFrame(
        {'recipe_id': recipe_ids, 'ingredient': all_ingredients, 'amount': all_amounts, 'unit': all_units,
         'descriptor': all_descriptors})

    ingredient_table['index'] += 1
    ingredient_table = ingredient_table.rename(columns={'index': 'ingredient_id'})
    recipe_ingredient_table = recipe_ingredient_table.merge(ingredient_table, left_on='ingredient',
                                                            right_on='ingredient')

    recipe_ingredient_table.drop('ingredient', axis=1, inplace=True)
    recipe_ingredient_table = recipe_ingredient_table.sort_values(by=['recipe_id'])

    recipe_ingredient_table= recipe_ingredient_table.reset_index()
    recipe_ingredient_table['index'] += 1
    recipe_ingredient_table = recipe_ingredient_table.rename(columns={'index': 'id'})

    recipe_ingredient_table.to_csv(_CLEANED_DATA_DIR.joinpath('recipe_ingredients.csv'), index = False)
    ingredient_table.to_csv(_CLEANED_DATA_DIR.joinpath('ingredients.csv'), index=False)


if __name__ == '__main__':
    
    if not Path.exists(_DATA_DIR):
        Path.mkdir(_DATA_DIR)

    if not Path.exists(_CLEANED_DATA_DIR):
        Path.mkdir(_CLEANED_DATA_DIR)

    #recipe_list = scrape_db()
    #new_data, bad_slugs = get_extra_data(recipe_list)

    with (_DATA_DIR / 'bodybuilding_recipes_all_info.json').open() as f:
        scraped_data = json.load(f)

    for recipe in scraped_data:
    #print(scraped_data[0])
        capture = flatten_json(recipe)
  
    #test = pd.DataFrame.from_dict(capture, orient='index')

    #print(test)

    #save_df()
    #process_ingredients(scraped_data)
    #process_nutrition(scraped_data)
    #process_instructions(scraped_data)
    #process_recipe_table(scraped_data)
