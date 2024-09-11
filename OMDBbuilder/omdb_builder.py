import pymysql
from typing import List
from pymysql import cursors

from OMDBbuilder.load_omdb_data import load_omdb_data
from OMDBbuilder.prepare_data import prep_omdb, prep_genre, prep_ratings
from OMDBbuilder.build_table import build_omdb_tbl, build_genre_tbl, build_ratings_tbl
from OMDBbuilder.tests import test_for_movieid_discrepancies


def gnr8_table_from_omdb_data(table_name: str,
                              cursor: pymysql.cursors.Cursor,
                              omdb_data: List[List[int | str |
                                                   float | None]]
                              ) -> None:
    valid_table_entries = ['omdb', 'genres', 'critic_ratings', 'all']

    if table_name not in valid_table_entries:
        raise Exception("Value entered for 'table_name' not valid. The"
                        " generation of the specified table has not yet"
                        " been here coded for.")
    elif table_name == 'all':
        prepped_omdb_data = prep_omdb(omdb_data)
        build_omdb_tbl(cursor, prepped_omdb_data)
        prepped_genre_data = prep_genre(omdb_data)
        build_genre_tbl(cursor, prepped_genre_data)
        prepped_ratings_data = prep_ratings(omdb_data)
        build_ratings_tbl(cursor, prepped_ratings_data)

    elif table_name == 'omdb':
        prepped_omdb_data = prep_omdb(omdb_data)
        build_omdb_tbl(cursor, prepped_omdb_data)

    elif table_name == 'genre':
        prepped_genre_data = prep_genre(omdb_data)
        build_genre_tbl(cursor, prepped_genre_data)

    elif table_name == 'critic_ratings':
        prepped_ratings_data = prep_ratings(omdb_data)
        build_ratings_tbl(cursor, prepped_ratings_data)


def build_out_omdb_tables(omdb_load_method: str,
                          db: pymysql.connections.Connection,
                          which_table: str = 'all',
                          omdb_as_dicts: bool = False
                          ) -> None:
    """Gets OMDB data for the movies in the 'allmovies' MySQL table,
    then creates the OMDB-related tables in that same db. (These include
    'omdb', 'genres', and 'critic_ratings'.)"""

    # Create a cursor from the db.
    cursor = db.cursor()

    # Read in the OMDB data, largely unprocessed, by requesting through
    # their API or by loading from file the previous requests.
    omdb_data = load_omdb_data(omdb_load_method, cursor,
                                  raw=omdb_as_dicts)

    # Check for discrepancies between unpickled OMDB data and allmovies
    # table (from MySQL.)
    if not omdb_as_dicts:
        test_for_movieid_discrepancies(cursor, omdb_data)

    # Create the OMDB-related tables in the MySQL db. At time of writing
    # these include 'omdb', 'genres', and 'critic_ratings'. Create all
    # these by specifying 'all'.
    gnr8_table_from_omdb_data(which_table, cursor, omdb_data)

    # Commit the changes to the db.
    db.commit()
