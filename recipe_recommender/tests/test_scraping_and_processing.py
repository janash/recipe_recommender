"""
Tests for scraping and processing
"""
import pytest

import recipe_recommender as rr

@pytest.fixture()
def testing_data():
    data = rr.scraping_and_processing.bodybuilding.scrape_db(test=True)
    return data

def test_bodybuilding_scrape(testing_data):
    """
    Test that pulling single recipe from bodybuilding database works.
    """
    data = testing_data

    # Write more tests here to see this data is what we expect (TODO)

def test_bodybuilding_process():
    """
    Test that processing is done correctly
    """

    data = testing_data

    # TODO
