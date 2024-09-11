import pickle
import urllib.parse
from typing import List, Dict

import pymysql
import requests as requests
import os


def download_omdb_data(cursor: pymysql.cursors.Cursor
                       ) -> (List[Dict[str, str | int]],
                                List[str | int | List[Dict[str, str]]]):
    """Queries all movie records (from table allMovies) and gets OMDB
    API records for each one. Each OMDB record is a dictionary, in the
    style of a JSON file. This method returns a list of those original
    dict records, as well as a list of lists representing their
    abbreviated versions."""

    omdb_data_raw = []
    omdb_data = []
    pull_counter = 0

    # Reading my OMDB API key from file, which is required for its use.
    key_file = "C:/Users/maxru/Programming/Python/.secret/OMDB_API.txt"
    with open(key_file) as f:
        omdb_api_key = f.read()

    # Querying all movies from the allMovies table in the MySQL db.
    query_all_titles = "SELECT Movie_ID, Title, Year FROM allMovies"
    cursor.execute(query_all_titles)

    # Tracking the failed OMDB API requests in a list
    erroneous_omdb_pulls = []

    # Iterate through the cursor's result to request each movie's OMDB
    # record, one-by-one.
    for (Movie_ID, Title, Year) in cursor:
        curr_title = urllib.parse.quote_plus(Title)

        # The OMDB API request works by taking the title and year of
        # the film in question. If either don't match closely, then the
        # request fails.
        # A couple films from my Evernote movie list require special
        # treatment for their titles, in order to reconcile them with
        # those of OMDB.

        # OMDB API can only handle the English translation of the
        # following famous Spanish-titled film.
        if Title == 'Y Tu Mama Tambien':
            curr_title = urllib.parse.quote_plus('And Your Mother Too')

        # Lydia Tar needs special treatment for her HTML request
        if curr_title == 'T%C3%83%C2%A1r':
            curr_title = 'T%C3%A1r'

        # A French movie is only accepted by its original French title
        # in OMDB.
        if Title == 'Sirocco and the Kingdom of the Winds':
            curr_title = urllib.parse.quote_plus("Sirocco et le royaume"
                                                 " des courants d'air")

        curr_year = str(Year)
        m_id = Movie_ID

        omdb_raw_record = requests.get(
            'http://www.omdbapi.com/?i=tt3896198&apikey=' + omdb_api_key
            + '&t=' + curr_title + '&y=' + str(curr_year)).json()

        # A counter tracks how many requests have been made.
        pull_counter += 1

        # If a request has failed, that movie's title and year are added
        # to a list that is later reported to the user. Then the loop
        # proceeds to the next movie record in the cursor.
        if omdb_raw_record['Response'] == 'False':
            erroneous_omdb_pulls.append((curr_title, curr_year))
            continue

        # Successful OMDB returns are appended to a list in their
        # complete detail, which is extensive.
        omdb_data_raw.append(omdb_raw_record)

        # A shortened version of the OMDB return is appended to a
        # different list. These are fields that struck me as the most
        # pertinent to analyses of (my) interest.
        omdb_record = [m_id,
                       Title, curr_year,
                       omdb_raw_record['Released'],
                       omdb_raw_record['Runtime'],
                       omdb_raw_record['Genre'],
                       omdb_raw_record['Director'],
                       omdb_raw_record['Writer'],
                       omdb_raw_record['Actors'],
                       omdb_raw_record['Ratings'],
                       omdb_raw_record.get('BoxOffice', 0)]

        omdb_data.append(omdb_record)

        # Report partial progress to the user when 50 additional
        # requests have been made.
        if pull_counter % 50 == 0:
            print(f'{pull_counter} movies processed so far.')

    # Report the total number of requests made, once complete.
    print(f'COMPLETE: {pull_counter} movies processed in total.\n')

    # Report the movies associated with failed requests to the user.
    if erroneous_omdb_pulls:
        print("FAILED REQUESTS:\n")
        for i in erroneous_omdb_pulls:
            print(i)

    # Save these returned OMDB records to file, via Pickling.
    pickle_omdb_data(omdb_data_raw, omdb_data)

    # Return both lists, of the complete OMDB records and the shortened
    # ones.
    return omdb_data_raw, omdb_data


def pickle_omdb_data(omdb_data_raw: List[List[Dict[str, str | int]]],
                     omdb_data: List[List[str |
                                          int |
                                          List[Dict[str, str]]]]
                     ) -> None:
    """Pickle (save to file) the OMDB records, both the raw and the
    shortened datasets."""

    # Get filepath to the 'data' folder, in which we store these files.
    data_dir_path = os.path.join(os.path.dirname(__file__), '../data/')

    # The names of the raw and feature-selected data files.
    raw_omdb_data_filename = 'OMDB_raw.pickle'
    omdb_data_filename = 'OMDB_3D_list.pickle'

    raw_omdb_data_path = os.path.join(data_dir_path,
                                      raw_omdb_data_filename)
    omdb_data_path = os.path.join(data_dir_path,
                                  omdb_data_filename)

    with open(raw_omdb_data_path,
              'wb') as f:
        pickle.dump(omdb_data_raw, f)

    with open(omdb_data_path,
              'wb') as f:
        pickle.dump(omdb_data, f)


def unpickle_omdb_data(raw: bool = False) -> (List[List[Dict[str, str | int]]],
                                              List[List[str |
                                                        int |
                                                        List[Dict[str, str]]]]):
    """Unpickles film data that was previously retrieved from OMDB
    (the Open Movie DataBase) through its API, via
    download_omdb_data()."""

    data_dir_path = os.path.join(os.path.dirname(__file__), '../data/')

    raw_omdb_data_filename = 'OMDB_raw.pickle'
    omdb_data_filename = 'OMDB_3D_list.pickle'

    raw_omdb_data_path = os.path.join(data_dir_path,
                                      raw_omdb_data_filename)
    omdb_data_path = os.path.join(data_dir_path,
                                  omdb_data_filename)

    unpickled_data = None

    if raw:
        with open(raw_omdb_data_path,
                  'rb') as f:
            unpickled_data = pickle.load(f)

    else:
        with open(omdb_data_path,
                  'rb') as f:
            unpickled_data = pickle.load(f)

    return unpickled_data
