# Healthy recipe recommendations

This is a personal project meant to help with healthy meal planning. We will be recommending recipes for meal prep based on macronutrients, and similarity to other recipes (maybe unhealthy ones).

This project uses python 3 and a PostgreSQL database.


## Data
The data we are using is scraped from bodybuiling.com recipes. We have the following information:

- *Recipes:* The master table includes recipes and their IDs. We have about 1700 unique recipes and descriptions. Each recipe has a tag (dinner, breakfast, lunch, etc.), but this has not yet been scraped and incorporated
- *Ingredients:* Maps ingredients and amounts to recipes. We have removed descriptions like 'chopped' or 'sliced', but some duplicates still remain
- *Nutrition:* Information about the macronutrients in each recipe. Includes carbohydrates, calories, protein for each recipe.
-*Cooking instructions:* We have prep and cook times for each recipe, as well as instructions in paragraph form.

## Database Structure
We will likely be using a PostgreSQL database to store the data with the following database structure.
- `recipes`
  - `recipe_id`
  - `recipe_name`
  - `description`
  - `tag`
- `recipe_ingredients`
    - `recipe_id`
    - `ingredient_id`
    - `amount`
    - `unit`
    - `descriptor`
- `recipe_nutrition`
  - `recipe_id`
  - `calories (kcal)`
  - `carbohydrates (g)`
  - `protein (g)`
  - `fat (g)`
- `ingredients`
  - `ingredient_id`
  - `ingredient_name`
- `cooking_instructions`
  - `recipe_id`
  - `prep_time`
  - `cook_time`
  - `instructions`

## Set-up
We store the data in a PostgresSQL database. You can install postgres on macOS using homebrew [instructions here].(https://launchschool.com/blog/how-to-install-postgresql-on-a-mac)

Once you have postgres installed, create the database by typing `createdb recipes`.

A nifty tool to view your database is [TablePlus](https://tableplus.io/). There's a free version that you can use to connect to up to two databases at a time.

Run the scripts in `recipes` to load the data into the database.
