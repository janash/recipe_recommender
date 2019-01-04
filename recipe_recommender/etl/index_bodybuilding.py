import os
import datetime
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Date, ForeignKey, ARRAY, Float, Boolean, Interval, create_engine
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd

from recipe_recommender.etl.utils import DB_URI

Base = declarative_base()


class Recipes(Base):
    __tablename__ = 'recipes'

    recipe_id = Column(String, primary_key=True)
    recipe_name = Column(String)
    description = Column(String)
   #tag = Column(String)

class Ingredients(Base):
    __tablename__ = 'ingredients'

    ingredient_id = Column(Integer, primary_key=True)
    ingredient = Column(String)


class RecipeIngredients(Base):
    __tablename__ = 'recipe_ingredients'

    id = Column(BigInteger, primary_key=True)

    # recipe_id = Column(String, ForeignKey('recipes.recipe_id'))
    recipe_id = Column(String)
    ingredient_id = Column(Integer, ForeignKey('ingredients.ingredient_id'))
    amount = Column(Float)
    unit = Column(String)
    descriptor = Column(String)

class RecipeNutrition(Base):
    __tablename__ = 'recipe_nutrition'

    recipe_id = Column(String, primary_key=True)
    servingSize = Column(String)
    calories = Column(Float)
    carbohydrates = Column(Float)
    protein = Column(Float)
    fat = Column(Float)

class RecipeDirections(Base):
    __tablename__ = 'recipe_directions'

    recipe_id = Column(String, primary_key=True)
    cookTime = Column(Float)
    totalTime = Column(Float)
    directions = Column(String)

if __name__ == '__main__':
    engine = create_engine(DB_URI)
    session = Session(bind=engine)

    _current_dir = os.path.dirname(os.path.abspath(__file__))
    _data_dir = os.path.join(_current_dir, "..", "..", "data", "cleaned")

    recipes = pd.read_csv(os.path.join(_data_dir, 'recipes.csv'))
    ingredients = pd.read_csv(os.path.join(_data_dir, 'ingredients.csv'))
    recipe_ingredients = pd.read_csv(os.path.join(_data_dir, 'recipe_ingredients.csv'))
    recipe_nutrition = pd.read_csv(os.path.join(_data_dir, 'recipe_nutrition.csv'))
    recipe_directions = pd.read_csv(os.path.join(_data_dir, 'recipe_directions.csv'))

    # Blow our DB up
    Base.metadata.drop_all(engine)
    # Generate our DB schema
    Base.metadata.create_all(engine)

    print('inserting...')

    recipes = recipes.to_dict('records')
    ingredients = ingredients.to_dict('records')
    recipe_ingredients = recipe_ingredients.to_dict('records')
    recipe_nutrition = recipe_nutrition.to_dict('records')
    recipe_directions = recipe_directions.to_dict('records')

    session.bulk_insert_mappings(Recipes, recipes)
    session.bulk_insert_mappings(Ingredients, ingredients)
    session.bulk_insert_mappings(RecipeIngredients, recipe_ingredients)
    session.bulk_insert_mappings(RecipeNutrition, recipe_nutrition)
    session.bulk_insert_mappings(RecipeDirections, recipe_directions)


    session.commit()
    session.close()
