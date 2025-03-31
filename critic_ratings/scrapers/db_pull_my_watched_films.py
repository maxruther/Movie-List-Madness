import pandas as pd
from sqlalchemy import create_engine, types

from mc_search_and_scrape import mc_search_and_scrape

def db_pull_my_watched_films():

    movie_db_url = None
    with open('.secret/movie_db_url.txt', 'r') as f:
        movie_db_url = f.read().strip()

    engine = create_engine(movie_db_url)
    # engine = create_engine('mysql://root:yos@localhost/moviedb')
    conn = engine.connect()

    watched_films_query = """
    SELECT aw.Title, omdb.Year as 'Release Year', omdb.Directors as Director
    FROM allwatched aw INNER JOIN omdb
    ON aw.Title=omdb.Title;
    """

    watched_films_df = pd.read_sql_query(watched_films_query, engine)
    watched_films_df.to_pickle('data/pkl/my_watched_films/my_watched_films.pkl')
    watched_films_df.to_csv('data/csv/my_watched_films/my_watched_films.csv', index=False)

    # # print(watched_films_df)

    # mc_search_and_scrape(
    #     watched_films_df,
    #     output_filename='mywatched',
    #     test_n_films=3,
    #     )

    # mywatches_mc_crs_df = pd.read_pickle('data/scraped/mywatches_mc_crs.pkl')
    # print(mywatches_mc_crs_df.head(5))

    # # Fix a couple variable types
    # mywatches_mc_crs_df['Score'] = mywatches_mc_crs_df['Score'].astype(int)
    # mywatches_mc_crs_df['Date Written'] = pd.to_datetime(mywatches_mc_crs_df['Date Written'], format='%b %d, %Y')

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


    # mywatches_mc_crs_df.to_sql(con=conn, 
    #                         name='mc_reviews', 
    #                         if_exists='replace',
    #                         index=False,
    #                         dtype=dtype_mapping,
    #                         )


if __name__ == '__main__':
    db_pull_my_watched_films()