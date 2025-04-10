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
        case 'mc_reviews':
            # Fix a couple variable types
            scrape_df['Score'] = scrape_df['Score'].astype('Int32')
            scrape_df['Date Written'] = pd.to_datetime(scrape_df['Date Written'], format='%b %d, %Y')

            # Define the variable type mapping for the MySQL table
            dtype_mapping = {
                'Title': types.VARCHAR(80),
                'Year': types.INT,
                'Publication': types.VARCHAR(80),
                'Score': types.INT,
                'Critic': types.VARCHAR(80),
                'Snippet': types.TEXT,
                'Date Written': types.DATE,
            }
        
        case 'mc_info':
            # Fix a couple variable types
            scrape_df['Runtime'] = scrape_df['Runtime'].astype(int)
            scrape_df['Year Searched'] = scrape_df['Year Searched'].astype('Int32')
            scrape_df['Year Result'] = scrape_df['Year Result'].astype('Int32')

            # Define the variable type mapping for the MySQL table
            dtype_mapping = {
                'Title Searched': types.VARCHAR(80),
                'Year Searched': types.INT,
                'Director Searched': types.VARCHAR(80),
                'Link Retrieved': types.TEXT,
                'Title Result': types.VARCHAR(80),
                'Year Result': types.INT,
                'Director Result': types.VARCHAR(80),
                'Metascore': types.FLOAT,
                'Runtime': types.INT,
                'Summary': types.TEXT,
                'Writers': types.TEXT,
            }

        case 'mc_searchresults':
            # Fix a couple variable types
            scrape_df['Year Searched'] = scrape_df['Year Searched'].astype('Int32')
            scrape_df['Year Result'] = scrape_df['Year Result'].astype('Int32')

            # Define the variable type mapping for the MySQL table
            dtype_mapping = {
                'Title Searched': types.VARCHAR(80),
                'Year Searched': types.INT,
                'Director Searched': types.VARCHAR(80),
                'Link': types.TEXT,
                'Title Result': types.VARCHAR(80),
                'Year Result': types.INT,
                'Director Result': types.VARCHAR(80),
                'Directors Fuzzy Sim': types.FLOAT,
                'Directors Cosine Sim': types.FLOAT,
                'Titles Fuzzy Sim': types.FLOAT,
                'Titles Cosine Sim': types.FLOAT,
            }
    
    return scrape_df, dtype_mapping


def load_mc_scrapes(
        *input_filepaths: str,
        ) -> None:

    for input_filepath in input_filepaths:
        print(f"\nProcessing file {input_filepath} for database loading.\n")

        if input_filepath == 'master':
            input_dirname = 'data/pkl/metacritic/master_files'
            input_filename = 'master'
        else:
            input_filename, input_extension = splitext(basename(input_filepath))
            input_dirname = dirname(input_filepath) + '/mc_scrape'

            if input_extension != '.pkl':
                raise ValueError(f"Input file must be a .pkl file. Detected extension: {input_extension}")

            if input_dirname[:9] != 'data/pkl/':
                raise ValueError(f"Input file must be in 'data/pkl/' or a subdirectory thereof. Detected directory: {input_dirname}")

            if not exists(input_filepath):
                raise FileNotFoundError(f"Input file does not exist: {input_filepath}")


        # Connect to the MySQL db
        movie_db_url = None
        with open('.secret/movie_db_url.txt', 'r') as f:
            movie_db_url = f.read().strip()
        engine = create_engine(movie_db_url)
        conn = engine.connect()


        # For each type of Metacritic scrape, load the data into a new table
        # in the MySQL db.
        for scrape_type in ['mc_reviews', 'mc_info', 'mc_searchresults']:
            scrape_df_filename = f'{input_filename}_{scrape_type}'
            scrape_df_filepath = f'{input_dirname}/{scrape_df_filename}.pkl'

            scrape_df = pd.DataFrame()
            if not os.path.exists(scrape_df_filepath):
                raise FileNotFoundError(f"Input file does not exist: {scrape_df_filepath}")
            else:
                scrape_df = pd.read_pickle(scrape_df_filepath)


            if scrape_df.empty:
                print(f"The {scrape_type} file is empty for '{input_filename}'.",
                "\nEnding this file's processing without loading to database.")
            else:
                print(f"\tLoading {scrape_type} data for '{input_filename}' into the database.")

                # # LOAD DATA TO A NEW TABLE IN THE MYSQL DB

                # Prepare the DataFrame for loading into MySQL
                scrape_df, dtype_mapping = prepare_scrape_df(
                    scrape_df,
                    scrape_type,
                    )
                
                # Load the prepared DataFrame into a MySQL table, 
                # overwriting it if it exists already.
                scrape_df.to_sql(con=conn, 
                                name=f'{scrape_df_filename}', 
                                if_exists='replace',
                                index=False,
                                dtype=dtype_mapping,
                                )
                
                print(f"\tSuccessfully loaded table '{scrape_df_filename}'.\n")


if __name__ == '__main__':

    load_mc_scrapes(
        # 'data/pkl/ebert/ebert_recent_reviews.pkl',
        # 'data/pkl/siskel/siskel_show_info.pkl',
        # 'data/pkl/musicbox/musicbox_show_info.pkl',
        # 'data/pkl/my_watched_films/my_watched_films.pkl',
        'master',
        )
