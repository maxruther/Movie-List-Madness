import pymysql
from ReadInEvernote import read_evernote_tables_to_3D_list
from SQLStatingMovieData import recreate_tables_with_data


def evernote_to_mysql(evernote_path: str,
                      db: pymysql.connections.Connection,
                      ) -> None:

    # Read tables from Evernote HTML file into a 3D python list.
    ingested_movie_data = read_evernote_tables_to_3D_list(evernote_path)

    # From that read-in movie list data, (re)generate tables in MySQL.
    recreate_tables_with_data(ingested_movie_data, db)
