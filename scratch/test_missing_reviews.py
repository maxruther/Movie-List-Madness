import pymysql
from movielist_ingestion.evernote_to_mysql import evernote_to_mysql
from omdb_builder.build_out_omdb import build_out_omdb_tables
from critic_ratings.fix_critic_ratings_tbl import fix_critic_ratings_tbl
from critic_ratings.report_missing_ratings import report_na_ratings_pre_fill

# Connect to my MySQL movie database
my_db = pymysql.connect(
    host="localhost",
    user="root",
    password="yos",
    database="movieDB"
)

"""
The purpose of this script is to report which movies are missing ratings from the various """


# Specify filepath of the MovieList html file, as exported from
# Evernote.

movie_list_file = "Movies\\Movies.html"

# Read in that movie list's data (to a multidimensional list) and
# write its table to the MySQL database.
evernote_to_mysql(movie_list_file, my_db)

# Retrieve supplemental movie data from OMDB, the "Online Movie
# Database," and write it to additional tables in the MySQL database.

# build_out_omdb_tables('load from file', my_db)
build_out_omdb_tables('request through OMDB API', my_db)

# Close the pymysql connection to the movie list database but also
# specify the database's filepath, to reconnect via SQLAlchemy, a method
# more advantageous to a method closely following.
my_db.close()
db_path = 'mysql://root:yos@localhost/moviedb'

# Implement some fixes to the table of critics' movie ratings. These
# fixes include filling in some scores that were erroneously missed by
# OMDB, as well as adding additional reviewers' scores, like from
# RogerEbert.com .
report_na_ratings_pre_fill(db_path)