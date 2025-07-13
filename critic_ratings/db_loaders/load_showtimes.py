from typing import Tuple, Dict
from sqlalchemy.types import TypeEngine

import pandas as pd

from sqlalchemy import create_engine, types
from os.path import splitext, basename, dirname, exists

from utils import load_latest_data

def prepare_scrape_df(
        show_scrape_df: pd.DataFrame,
        ) -> Tuple[ pd.DataFrame, Dict[str, TypeEngine] ]:
    
    year_attr = None
    if 'Year' in show_scrape_df.columns:
        year_attr = 'Year'
    elif 'Release Year' in show_scrape_df.columns:
        year_attr = 'Release Year'

    # Fix variable type(s)
    show_scrape_df[year_attr] = show_scrape_df[year_attr].astype('Int32')
    
    # Define the variable type mapping for the MySQL table
    dtype_mapping = {
        'Title': types.VARCHAR(80),
        year_attr: types.INT,
        'Director': types.VARCHAR(80),
        'Showtime': types.DATETIME,
        'Theater': types.VARCHAR(80),
        'Scrape_Datetime': types.DATETIME,
    }
    
    return show_scrape_df, dtype_mapping

def load_showtimes() -> None:

    theater_list = [
        'siskel',
        'musicbox',
    ]

    scrape_type_list = [
        'show_info',
        'showtimes'
    ]

    for scrape_type in scrape_type_list:
        for theater in theater_list:
            show_scrape_df = load_latest_data(theater, scrape_type)
            dataset_name = f'{theater}_{scrape_type}'

            if show_scrape_df.empty:
                raise Exception(f"DB LOAD ERROR: The loaded dataframe for '{dataset_name}' is empty. Ending this file's processing without loading to database.\n")
            else:
                print(f"Loading showtime data for '{dataset_name}' into the database.")

                # # LOAD DATA TO A NEW TABLE IN THE MYSQL DB

                # Prepare the DataFrame for loading into MySQL
                show_scrape_df, dtype_mapping = prepare_scrape_df(
                    show_scrape_df,
                    )
                
                # Connect to the MySQL db
                movie_db_url = None
                with open('.secret/movie_db_url.txt', 'r') as f:
                    movie_db_url = f.read().strip()
                engine = create_engine(movie_db_url)
                conn = engine.connect()
                
                # Load the prepared DataFrame into a MySQL table, 
                # overwriting it if it exists already.
                show_scrape_df.to_sql(con=conn, 
                                name=f'{dataset_name}', 
                                if_exists='replace',
                                index=False,
                                dtype=dtype_mapping,
                                )

                print(f"Successfully loaded table '{dataset_name}'.\n")


if __name__ == '__main__':

    load_showtimes()

