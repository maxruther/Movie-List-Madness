import pymysql
from ReadInEvernote import read_evernote_tables_to_3D_list
from SQLStatingMovieData import *

# Connect to my MySQL movie database
mydb = pymysql.connect(
    host="localhost",
    user="root",
    password="yos",
    database="movieDB"
)

# Create a cursor for this database
myCursor = mydb.cursor()

# Read in the movie list data from the Evernote-exported HTML file.
# movieFile = "Movies\\Movies 2024-01-28.html"
movieFile = "Movies\\Movies.html"

ingested_movie_data = read_evernote_tables_to_3D_list(movieFile)

# Regenerate tables in MySQL from the read-in movie list data.
recreate_tables_with_data(ingested_movie_data, myCursor, mydb)

mydb.commit()

myCursor.close()
mydb.close()
