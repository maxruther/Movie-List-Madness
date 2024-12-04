import pymysql
from .read_from_evernote_html import read_evernote_tbls_to_3d_list
from .write_to_mysql import build_core_mysql_tbls


def evernote_to_mysql(evernote_path: str,
                      db: pymysql.connections.Connection,
                      ) -> None:

    # Read tables from Evernote HTML file into a 3D python list.
    ingested_movie_data = read_evernote_tbls_to_3d_list(evernote_path)

    # From that read-in movie list data, (re)generate tables in MySQL.
    build_core_mysql_tbls(ingested_movie_data, db)
