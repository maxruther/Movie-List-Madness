import pymysql
from movie_list_ingestor import evernote_to_mysql
from OMDBbuilder.omdb_builder import build_out_omdb_tables
from fix_critic_ratings_table import fix_critic_ratings_table

# Connect to my MySQL movie database
my_db = pymysql.connect(
    host="localhost",
    user="root",
    password="yos",
    database="movieDB"
)

# Read in the movie list data from the Evernote-exported HTML file.
# movieFile = "Movies\\Movies 2024-01-28.html"
movieFile = "Movies\\Movies.html"

evernote_to_mysql(movieFile, my_db)
# build_out_omdb_tables('load from file', my_db)
build_out_omdb_tables('request from OMDB', my_db)

my_db.close()

# To connect to the MySQL db via SQLAlchemy (which is how
# fix_critic_ratings_table.py connects.)
db_path = 'mysql://root:yos@localhost/moviedb'

fix_critic_ratings_table(db_path)
