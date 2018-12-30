import datetime
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Date, ForeignKey, ARRAY, Float, Boolean, Interval
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import pandas as pd

from .utils import DB_URI

Base = declarative_base()
#
# class Recipes(Base):
#     __tablename__ = 'recipes'
#
#     recipe_id = Column(String, primary_key=True)
#     recipe_name = Column(String)
#     description = Column(String)
#     tag = Column(String)

class Ingredients(Base):
    __tablename__ = 'ingredients'

    ingredient_id = Column(Integer, primary_key=True)
    ingredient = Column(String)

# class RecipeIngredients(Base):
#     __tablename__ = 'recipe_ingredients'
#
#     id = Column(BigInteger, primary_key=True)
#
#     recipe_id = Column(String, ForeignKey('recipes.recipe_id'))
#     ingredient_id = Column(Integer, ForeignKey('ingredients.ingredient_id'))
#     amount = Column(Float)
#     unit = Column(String)

if __name__ == '__main__':
    print('db uri ', DB_URI )
    engine = create_engine(DB_URI)
    session = Session(bind=engine)
    # sessionmaker(bind=engine)


    ingredients = pd.read_csv('../../data/cleaned/ingredients.csv')

    # Blow our DB up
    Base.metadata.drop_all(engine)
    # Generate our DB schema
    Base.metadata.create_all(engine)

    print('inserting...')
    ingredients.ingredient = ingredients.ingredient.astype(str)
    ingredients.ingredient_id = ingredients.ingredient_id.astype(int)

    ingredients = ingredients.to_dict('records')

    session.bulk_insert_mappings(Ingredients, ingredients)


    session.commit()
    session.close()
