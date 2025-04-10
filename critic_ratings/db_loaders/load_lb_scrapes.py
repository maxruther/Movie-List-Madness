from typing import Tuple, Dict
from sqlalchemy.types import TypeEngine

import pandas as pd

import os

from sqlalchemy import create_engine, types
from os.path import splitext, basename, dirname, exists


def prepare_scrape_df(
        scrape_df: pd.DataFrame,
        scrape_type: str,
        ) -> Tuple[ pd.DataFrame, Dict[str, TypeEngine] ]:

    dtype_mapping = {}
    match scrape_type:

        case 'lb_diary':
            # Fix a couple variable types
            scrape_df['Year'] = scrape_df['Year'].astype('Int32')

            # Define the variable type mapping for the MySQL table
            dtype_mapping = {
                'Title': types.VARCHAR(80),
                'Year': types.INT,
                'Director': types.VARCHAR(80),
                'Rating': types.FLOAT,
                'Watch Date': types.DATE,
            }
        
        case 'lb_friend_ratings':
            # Fix a couple variable types
            scrape_df['Year'] = scrape_df['Year'].astype('Int32')

            # Define the variable type mapping for the MySQL table
            dtype_mapping = {
                'title': types.VARCHAR(80),
                'year': types.INT,
                # 'Director': types.VARCHAR(80),
                'link': types.TEXT,
            }
    
    return scrape_df, dtype_mapping


def load_lb_scrapes(
        *input_filepaths: str,
        ) -> None:

    for input_filepath in input_filepaths:
        print(f"\nProcessing file {input_filepath} for database loading.\n")


        input_filename, input_extension = splitext(basename(input_filepath))
        input_dirname = dirname(input_filepath)

        if input_extension != '.pkl':
            raise ValueError(f"Input file must be a .pkl file. Detected extension: {input_extension}")

        if input_dirname[:9] != 'data/pkl/':
            raise ValueError(f"Input file must be in 'data/pkl/' or a subdirectory thereof. Detected directory: {input_dirname}")

        if not exists(input_filepath):
            raise FileNotFoundError(f"Input file does not exist: {input_filepath}")
        

        lb_user_url, scrape_type = None, None
        testing = False
        if input_filename[-5:] == '_test':
            lb_user_url = input_filename.split('_')[-2]
            scrape_type = '_'.join(input_filename.split('_')[:-2])
            testing = True
        else:
            lb_user_url = input_filename.split('_')[-1]
            scrape_type = '_'.join(input_filename.split('_')[:-1])


        scrape_df = pd.DataFrame()
        if not os.path.exists(input_filepath):
            raise FileNotFoundError(f"Input file does not exist: {input_filepath}")
        else:
            scrape_df = pd.read_pickle(input_filepath)

        if scrape_df.empty:
            print(f"The '{scrape_type}' dataframe is empty for '{input_filename}'.",
            "\nEnding this file's processing without loading to database.")
        else:
            print(f"\tLoading the data of '{input_filename}' into the database.")


        # Connect to the MySQL db
        movie_db_url = None
        with open('.secret/movie_db_url.txt', 'r') as f:
            movie_db_url = f.read().strip()
        engine = create_engine(movie_db_url)
        conn = engine.connect()


        # # LOAD DATA TO A NEW TABLE IN THE MYSQL DB

        # Prepare the DataFrame for loading into MySQL
        scrape_df, dtype_mapping = prepare_scrape_df(
            scrape_df,
            scrape_type,
            )
        
        # Load the prepared DataFrame into a MySQL table, 
        # overwriting it if it exists already.
        scrape_df.to_sql(con=conn, 
                        name=f'{input_filename}', 
                        if_exists='replace',
                        index=False,
                        dtype=dtype_mapping,
                        )
        
        print(f"\tSuccessfully loaded table '{input_filename}'.\n")


if __name__ == '__main__':

    load_lb_scrapes(
        'data/pkl/letterboxd/lb_diary_yoyoyodaboy.pkl',
        'data/pkl/letterboxd/lb_friends_ratings_yoyoyodaboy.pkl',
        # 'data/pkl/letterboxd/lb_friends_ratings_yoyoyodaboy_test.pkl',
        )
