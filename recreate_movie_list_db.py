import pymysql
from movie_list_ingestor import evernote_to_mysql
from omdb_builder import create_omdb_tables
from amend_CR_table import fix_critic_ratings_table

# Connect to my MySQL movie database
mydb = pymysql.connect(
    host="localhost",
    user="root",
    password="yos",
    database="movieDB"
)

# Read in the movie list data from the Evernote-exported HTML file.
# movieFile = "Movies\\Movies 2024-01-28.html"
movieFile = "Movies\\Movies.html"

evernote_to_mysql(movieFile, mydb)
create_omdb_tables('load from file', mydb)

mydb.close()

# To connect to the MySQL db via SQLAlchemy (which is how
# amend_CR_table.py connects.)
db_path = 'mysql://root:yos@localhost/moviedb'

fix_critic_ratings_table(db_path)
