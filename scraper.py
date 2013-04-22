#!/usr/bin/env python

import datetime
from datetime import timedelta
from sets import Set

from bs4 import BeautifulSoup
import nltk
from pymongo import MongoClient, DESCENDING, ASCENDING
import requests

# Constants.
BASE_URL = 'http://dining.guckenheimer.com/clients/npr/FSS/fss.nsf/weeklyMenuLaunch/95RPBM~04-22-2013/$file/'
TODAY = datetime.date.today()
CATEGORIES = ["Breakfast Special", "All Salads Considered", "Custom Deli and Panini", "The Good Earth Grill", "Food of the Nation", "Serious Comfort Food"]
COLORS = [('FF0000', 0), ('FF9900', 1), ('009900', 2)]
COLOR_NAMES = ['red', 'yellow', 'green']
DAYS = [('mon', TODAY), ('tue', TODAY + timedelta(1)), ('wed', TODAY + timedelta(2)), ('thu', TODAY + timedelta(3)), ('fri', TODAY + timedelta(4))]
NOUNS = ['NNP', 'NN', 'NNS']
DEATH_TERMS = ["jasmine", "whole", "crusted", "blanc", "morrocan", "w/", "&", "grilled", "baked", "roasted", "gourmet", "wild", "side", "cordon", "bleu", "classic", "sharp", "slow", "fresh", "sundried", "cole", "national", "pulled"]

# Mongo connection objects.
client = MongoClient()
db = client.apps
menu_items = db.menu_items

# Make sure we have indexes.
menu_items.create_index([
    ('date', DESCENDING),
    ('day', ASCENDING),
    ('dietary_value', ASCENDING),
    ('category', ASCENDING),
    ('week', DESCENDING)
])

# Loop through the day names.
for day, day_date in DAYS:

    r = requests.get('%s%s.htm' % (BASE_URL, day))

    index = 0

    # Loop through the color codes.
    for hex_name, color_value in COLORS:

        soup = BeautifulSoup(r.content)
        spans = soup.select('span[style="color:#%s;"]' % hex_name)

        # Loop through the food items.
        for span in spans:

            item_dict = {}
            item_dict['description'] = span.contents[0]

            # Set the ingredients.
            ingredients = Set([])

            # Parse the part of speech using the NLTK positional tagger.
            for ingredient, speech_part in nltk.tag.pos_tag(span.contents[0].split()):
                is_noun = False

                # If this is one of the noun part-of-speech types, make it a noun.
                for noun_type in NOUNS:
                    if speech_part == noun_type:
                        is_noun = True

                # Prepare the term for storing.
                ingredient = ingredient\
                    .replace(',', '')\
                    .replace('!', '')\
                    .replace('buerre', 'butter')\
                    .strip()\
                    .lower()

                # That tagger isn't great. Help it out with some death terms.
                for death_term in DEATH_TERMS:
                    if ingredient == death_term:
                        is_noun = False

                # Add to the set if it ends up being a noun.
                if is_noun is True:
                    ingredients.add(ingredient)

            # Push the list to our item.
            item_dict['ingredients'] = list(ingredients)

            # Set up the price. For those with no price, set it to None and not 0.00.
            try:
                item_dict['price'] = span.contents[2]
            except IndexError:
                item_dict['price'] = None

            # Set the constants.
            item_dict['dietary_value'] = {}
            item_dict['dietary_value']['value'] = color_value
            item_dict['dietary_value']['color'] = COLOR_NAMES[color_value]

            item_dict['day'] = day
            item_dict['date'] = day_date.strftime("%Y-%m-%d")
            item_dict['week'] = int(day_date.strftime("%W"))

            # Set the category positionally.
            # I hope they don't have more than one thing
            # in the same category.
            item_dict['category'] = CATEGORIES[index]
            index += 1

            unique_dict = {}
            unique_dict['date'] = item_dict['date']
            unique_dict['category'] = item_dict['category']

            menu_items.update(unique_dict, item_dict, upsert=True, multi=False)
