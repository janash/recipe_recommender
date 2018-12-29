import datetime
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Date, ForeignKey, ARRAY, Float, Boolean, Interval
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import pandas as pd

from utils import DB_URI

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


if __name__ == '__main__':
    engine = create_engine(DB_URI)
    session = Session(bind=engine)

    recipes = pd.read_csv('../../data/cleaned/recipes.csv')
    ingredients = pd.read_csv('../../data/cleaned/ingredients.csv')
    recipe_ingredients = pd.read_csv('../../data/cleaned/recipe_ingredients.csv')

    # Blow our DB up
    Base.metadata.drop_all(engine)
    # Generate our DB schema
    Base.metadata.create_all(engine)

    print('inserting...')

    recipes = recipes.to_dict('records')
    ingredients = ingredients.to_dict('records')
    recipe_ingredients = recipe_ingredients.to_dict('records')

    session.bulk_insert_mappings(Recipes, recipes)
    session.bulk_insert_mappings(Ingredients, ingredients)
    session.bulk_insert_mappings(RecipeIngredients, recipe_ingredients)

    session.commit()
    session.close()
