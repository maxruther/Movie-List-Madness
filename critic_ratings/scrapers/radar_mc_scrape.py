import pandas as pd
import numpy as np

from mc_complete_scrape import mc_search_and_scrape
from sqlalchemy import create_engine, types


def radar_mc_scrape(
        target_film_df_filename: str,
        parent_dir: str,
        adding_to_existing_df=True,
        ) -> None:
    
    radar_film_df = pd.read_pickle(f'data/{parent_dir}/{target_film_df_filename}.pkl')

    mc_search_and_scrape(
        radar_film_df,
        cr_filename=f'{target_film_df_filename}_mc_crs',
        info_filename=f'{target_film_df_filename}_mc_info',
        searchresults_filename=f'{target_film_df_filename}_mc_searchresults',
        adding_to_existing_df=adding_to_existing_df,
        )


    radar_film_mc_crs_df = pd.read_pickle(f'data/scraped/{target_film_df_filename}_mc_crs.pkl')

    if radar_film_mc_crs_df.empty:
        print(f"The Metacritic CRs file is empty for the subject films, '{target_film_df_filename}'.\n")
    else:
        print(radar_film_mc_crs_df.head(5))

        # Fix a couple variable types
        radar_film_mc_crs_df['Score'] = radar_film_mc_crs_df['Score'].astype(int)
        radar_film_mc_crs_df['Date Written'] = pd.to_datetime(radar_film_mc_crs_df['Date Written'], format='%b %d, %Y')


    # # LOAD DATA TO A NEW TABLE IN THE MYSQL DB

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
    # mc_scrape_for_radar('ebert_radar', 'scraped')
    # radar_mc_scrape('musicbox_radar', 'showtimes')
    radar_mc_scrape('siskel_radar', 'showtimes')
    # radar_mc_scrape('siskel_radar', 'showtimes', adding_to_existing_df=False)
    
    # radar_mc_scrape('test_radar', 'showtimes', adding_to_existing_df=False)
