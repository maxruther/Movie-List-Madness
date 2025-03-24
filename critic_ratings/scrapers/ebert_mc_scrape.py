import pandas as pd
import numpy as np

from mc_complete_scrape import mc_search_and_scrape
from sqlalchemy import create_engine, types


def mc_scrape_for_radar(
        target_film_df_filename: str,
        parent_dir: str,
        ) -> None:
    
    radar_film_df = pd.read_pickle(f'data/{parent_dir}/{target_film_df_filename}.pkl')

    # print(pd.isna(radar_film_df[radar_film_df['Title'] == 'MUSIC BOX MOVIE TRIVIA']['Year']))

    mc_search_and_scrape(
        radar_film_df,
        cr_filename=f'{target_film_df_filename}_mc_crs',
        info_filename=f'{target_film_df_filename}_mc_info',
        searchresults_filename=f'{target_film_df_filename}_mc_searchresults',
        # adding_to_existing_df=False,
        )


    radar_film_mc_crs_df = pd.read_pickle(f'data/scraped/{target_film_df_filename}_mc_crs.pkl')
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
    mc_scrape_for_radar('musicbox_radar', 'showtimes')
