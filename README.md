# Healthy recipe recommendations

This is a personal project meant to help with healthy meal planning. We will be recommending recipes for meal prep based on macronutrients, and similarity to other recipes (maybe unhealthy ones).


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
