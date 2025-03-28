import pandas as pd

import os

from mc_search_and_scrape import mc_search_and_scrape
from sqlalchemy import create_engine, types


def radar_mc_scrape(
        input_pkld_df_filepath: str,
        adding_to_existing_df=True,
        test_n_films: int = 0,
        ) -> None:
    
    # radar_film_df = pd.read_pickle(f'data/{parent_dir}/{input_pkld_df_filepath}.pkl')
    radar_film_df = pd.read_pickle(input_pkld_df_filepath)

    input_filepath_partial = input_pkld_df_filepath.replace('data/pkl/', '')
    input_parentdirpath = input_filepath_partial[:input_filepath_partial.rfind('/')]
    input_filename = input_filepath_partial[input_filepath_partial.rfind('/') + 1:]
    input_filename = input_filename.replace('.pkl', '')

    mc_search_and_scrape(
        radar_film_df,
        output_filename=input_filename,
        output_parentdir=input_parentdirpath,
        adding_to_existing_df=adding_to_existing_df,
        test_n_films=test_n_films,
        )

    output_reviews_filename = input_filename
    if test_n_films:
        output_reviews_filename = 'test_' + output_reviews_filename


    radar_film_mc_crs_df = pd.read_pickle(f'data/pkl/{input_parentdirpath}/{output_reviews_filename}_mc_reviews.pkl')

    if radar_film_mc_crs_df.empty:
        print(f"The Metacritic CRs file is empty for the subject films, '{output_reviews_filename}'.\n")
    else:
        print(radar_film_mc_crs_df.head(5))

        # # LOAD DATA TO A NEW TABLE IN THE MYSQL DB

        # # Fix a couple variable types
        # radar_film_mc_crs_df['Score'] = radar_film_mc_crs_df['Score'].astype(int)
        # radar_film_mc_crs_df['Date Written'] = pd.to_datetime(radar_film_mc_crs_df['Date Written'], format='%b %d, %Y')

        # # Define the variable type mapping for the MySQL table
        # dtype_mapping = {
        #     'Title': types.VARCHAR(80),
        #     'Year': types.INT,
        #     'Publication': types.VARCHAR(80),
        #     'Score': types.INT,
        #     'Critic': types.VARCHAR(80),
        #     'Snippet': types.TEXT,
        #     'Date Written': types.DATE,
        # }

        # # Connect to MySQL db and create table
        # engine = create_engine('mysql://root:yos@localhost/moviedb')
        # conn = engine.connect()

        # radar_film_mc_crs_df.to_sql(con=conn, 
        #                            name=f'{target_film_df_filename}_cr_reviews', 
        #                            if_exists='replace',
        #                            index=False,
        #                            dtype=dtype_mapping,
        #                            )


if __name__ == '__main__':
    # radar_mc_scrape('data/pkl/ebert/ebert_recent_reviews.pkl',
    #                 test_n_films=10,
    #                 )
    
    # radar_mc_scrape('data/pkl/musicbox/musicbox_show_info.pkl')

    radar_mc_scrape('data/pkl/siskel/siskel_inferior_show_info.pkl',
                    test_n_films=15,
                    )

    pass