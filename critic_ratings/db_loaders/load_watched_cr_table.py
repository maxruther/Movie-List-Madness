import pandas as pd
import numpy as np

import pymysql
from sqlalchemy import create_engine

import os

from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
from sklearn.model_selection import cross_validate, train_test_split
from sklearn.metrics import classification_report, confusion_matrix

import matplotlib.pyplot as plt
import seaborn as sns


def load_watched_cr_table() -> None:
    """Takes the critical reviews scraped from Metacritic, joins them
    with my own reviews of my watches, then pivots that result wider
    so that every reviewer (including myself) is an attribute. (Every watched film is a row.)"""

    # Connect to the MySQL db
    movie_db_url = None
    with open('.secret/movie_db_url.txt', 'r') as f:
        movie_db_url = f.read().strip()
    engine = create_engine(movie_db_url)
    conn = engine.connect()

    # Load in the critic reviews scraped from Metacritic that related to my
    # watches (those listed in the processed Evernote movie list.)
    mc_review_query = """
    SELECT * FROM my_watched_films_mc_reviews
    """
    mcr_df = pd.read_sql_query(mc_review_query, engine)

    # Load in my own ratings of my watched movies
    query = "SELECT Title, Year, Rating FROM allwatched"
    aw_df = pd.read_sql_query(query, engine)


    # # # Transformation - Prepare datasets for merging

    # # Metacritic Review Data

    # Rename 'Title Searched' and 'Year Searched' to 'Title' and 'Year',
    # to match the names of those fields in my personal ratings dataset.
    mcr_df = mcr_df.rename(columns={'Title Searched': 'Title', 'Year Searched': 'Year'})

    # Transform the 'Score' field (the review scores) from an integer
    # in [0, 100] to a decimal in [0, 1].
    mcr_score_df = mcr_df[['Title','Year','Publication','Score']]

    # In the 'Title' field, change apostrophe's to single-quotes, to match
    # the punctuation in my personal ratings dataset.
    mcr_score_df.loc[:, 'Title'] = mcr_score_df.loc[:, 'Title'].str.replace('’', "'")

    # # My Ratings Data

    # Add 'Publication' attribute, to match that in the critic ratings set.
    aw_df['Publication'] = 'Max Ruther'

    # Create 'Score' field by remapping 'Rating' to numeric values (from an 
    # ordinal categorical.)
    my_rating_to_score = {
        'NOT FOR ME' : 0,        # 0 / 4 stars
        'GREAT': 0.625,          # 2.5 / 4 stars
        'PRETTY AWESOME': 0.875, # 3.5 / 4 stars
        'AWESOME': 1,            # 4 / 4 stars
    }
    aw_df['Score'] = aw_df['Rating'].map(my_rating_to_score)
    aw_score_df = aw_df.drop(columns='Rating')


    # # # Integration - Combine these two review score datasets

    # Concatenate the datasets along the index, now that their attributes
    # match.
    acr_df = pd.concat([aw_score_df, mcr_score_df], ignore_index=True)

    # Address ratings with duplicate movie and publication (these were
    # different reviewers weighing in.)
    dup_film_and_publ_df = acr_df[acr_df.duplicated(['Title', 'Year', 'Publication'], keep=False)]
    # I address these by averaging the review scores of each set of
    # duplicates.
    avgd_dups = dup_film_and_publ_df\
    .groupby(['Title', 'Year', 'Publication'], as_index=False)\
    .mean('Score')

    # From the unduplicated records, forming a separate df for imminent 
    # combination
    undupd = acr_df.drop_duplicates(['Title', 'Year', 'Publication'], keep=False)

    # Combine these sets through concatenation to create a deduplicated
    # version of the earlier integration.
    acr_dedupd = pd.concat([avgd_dups, undupd], axis=0).sort_values(by='Title', ascending=False)

    # Now that the those identifier fields are deduplicated, I can pivot 
    # wider on their basis, as I initially planned.
    acr_df3 = acr_dedupd.pivot(index=['Title', 'Year'], columns='Publication', values='Score').reset_index()
    acr_df3.columns.name = None
    # print(acr_df3.head(10))

    # # # Load the data to the db.
    table_name = 'crs_wide'

    acr_df3.to_sql(
        con=conn, 
        name=f'{table_name}', 
        if_exists='replace',
        index=False,
        # dtype=dtype_mapping,
        )

    print(f"\tSuccessfully loaded table '{table_name}'.\n")


if __name__ == '__main__':
    load_watched_cr_table()
