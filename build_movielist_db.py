import pymysql
from sqlalchemy import create_engine

from movielist_ingestion.evernote_to_mysql import evernote_to_mysql
from omdb_builder.build_out_omdb import build_out_omdb_tables
from critic_ratings.fix_critic_ratings_tbl import fix_critic_ratings_tbl

# Connect to my MySQL movie database

# Read in my database's creds/URL from a file.
host, user, password, database = None, None, None, None
with open('.secret/movie_db_creds_pymysql.txt', 'r') as f:
    host, user, password, database = f.read().strip().split('\n')

my_db = pymysql.connect(
    host=host,
    user=user,
    password=password,
    database=database,
)

# Specify filepath of the MovieList html file, as exported from
# Evernote.
# movie_list_file = "data\\movie_lists\\Movies 2024-01-28.html"
movie_list_file = "data\\movie_lists\\Movies.html"

# Read in that movie list's data (to a multidimensional list) and
# write its table to the MySQL database.
evernote_to_mysql(movie_list_file, my_db)

# Retrieve supplemental movie data from OMDB, the "Online Movie
# Database," and write it to additional tables in the MySQL database.
build_out_omdb_tables('load from file', my_db)
# build_out_omdb_tables('request through OMDB API', my_db)


# Close the pymysql connection to the movie list database but also
# specify the database's filepath, to reconnect via SQLAlchemy, a method
# more advantageous to a method closely following.
my_db.close()
# Read in my database's creds/URL from a file.
movie_db_url = f"mysql://{user}:{password}@{host}/{database}"

# Implement some fixes to the table of critics' movie ratings. These
# fixes include filling in some scores that were erroneously missed by
# OMDB, as well as adding additional reviewers' scores, like from
# RogerEbert.com .
# fix_critic_ratings_tbl(movie_db_url)
fix_critic_ratings_tbl(movie_db_url, na_report=True)
