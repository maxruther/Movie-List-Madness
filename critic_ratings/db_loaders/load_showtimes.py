from typing import Tuple, Dict
from sqlalchemy.types import TypeEngine

import pandas as pd

from sqlalchemy import create_engine, types
from os.path import splitext, basename, dirname, exists


def prepare_scrape_df(
        showtime_df: pd.DataFrame,
        ) -> Tuple[ pd.DataFrame, Dict[str, TypeEngine] ]:
    
    year_attr = None
    if 'Year' in showtime_df.columns:
        year_attr = 'Year'
    elif 'Release Year' in showtime_df.columns:
        year_attr = 'Release Year'

    # Fix variable type(s)
    showtime_df[year_attr] = showtime_df[year_attr].astype('Int32')
    
    # Define the variable type mapping for the MySQL table
    dtype_mapping = {
        'Title': types.VARCHAR(80),
        year_attr: types.INT,
        'Director': types.VARCHAR(80),
        'Showtime': types.DATETIME,
        'Showtime_Date': types.DATE,
        'Showtime_Time': types.TIME,
    }
    
    return showtime_df, dtype_mapping


def load_showtimes(
        *input_filepath_list: str,
        ) -> None:

    for input_filepath in input_filepath_list:
        print(f"\nProcessing file {input_filepath} for database loading.")

        input_filename, input_extension = splitext(basename(input_filepath))
        input_dirname = dirname(input_filepath)

        if input_extension != '.pkl':
            raise ValueError(f"Input file must be a .pkl file. Detected extension: {input_extension}")

        if input_dirname[:9] != 'data/pkl/':
            raise ValueError(f"Input file must be in 'data/pkl/' or a subdirectory thereof. Detected directory: {input_dirname}")

        if not exists(input_filepath):
            raise FileNotFoundError(f"Input file does not exist: {input_filepath}")

        showtime_df = pd.read_pickle(input_filepath)

        if showtime_df.empty:
            print(f"The showtime file is empty for '{input_filename}'.",
                "\nEnding this file's processing without loading to database.")
        else:
            print(f"Loading showtime data for '{input_filename}' into the database.")

            # # LOAD DATA TO A NEW TABLE IN THE MYSQL DB

            # Prepare the DataFrame for loading into MySQL
            showtime_df, dtype_mapping = prepare_scrape_df(
                showtime_df,
                )
            
            # Connect to the MySQL db
            movie_db_url = None
            with open('.secret/movie_db_url.txt', 'r') as f:
                movie_db_url = f.read().strip()
            engine = create_engine(movie_db_url)
            conn = engine.connect()
            
            # Load the prepared DataFrame into a MySQL table, 
            # overwriting it if it exists already.
            showtime_df.to_sql(con=conn, 
                            name=f'{input_filename}', 
                            if_exists='replace',
                            index=False,
                            dtype=dtype_mapping,
                            )

            print(f"Successfully loaded table '{input_filename}'.")


if __name__ == '__main__':

    load_showtimes(
        'data/pkl/siskel/siskel_showtimes.pkl',
        'data/pkl/musicbox/musicbox_showtimes.pkl',
        )
