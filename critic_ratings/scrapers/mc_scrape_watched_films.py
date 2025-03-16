import pandas as pd
from sqlalchemy import create_engine

from mc_complete_scrape import mc_search_and_scrape

engine = create_engine('mysql://root:yos@localhost/moviedb')
conn = engine.connect()

watched_films_query = """
SELECT aw.Title, omdb.Year as 'Release Year', omdb.Directors as Director
FROM allwatched aw INNER JOIN omdb
ON aw.Title=omdb.Title;"""

watched_films_df = pd.read_sql_query(watched_films_query, engine)

# print(watched_films_df)

mc_search_and_scrape(
    watched_films_df,
    cr_filename='mywatches_mc_crs',
    info_filename='mywatches_mc_info',
    searchresults_filename='mywatches_mc_searchresults')
