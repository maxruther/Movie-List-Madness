import urllib.parse

import pymysql
import requests as requests
import pickle
import copy
from typing import List, Dict
from pymysql import cursors


def unpickle_stored_omdb_recs() -> (List[List[Dict[str, str | int]]],
                                    List[List[str |
                                              int |
                                              List[Dict[str, str]]]]):
    """Unpickles film data that was previously retrieved from OMDB
    (the Open Movie DataBase) through its API, via
    pull_omdb_records()."""

    with open('C:/Users/maxru/eclipse-workspace/movie_list_dvlp/'
              'movie_list_parsing/pickled_OMDB_dicts.data',
              'rb') as f:
        all_omdb_dicts = pickle.load(f)

    with open('C:/Users/maxru/eclipse-workspace/movie_list_dvlp/'
              'movie_list_parsing/pickled_OMDBs_abrvd.data',
              'rb') as f:
        all_omdb_abrvd = pickle.load(f)

    return all_omdb_dicts, all_omdb_abrvd


def pickle_omdb_recs(all_omdb_dicts: List[List[Dict[str, str | int]]],
                     all_omdb_abrvd: List[List[str |
                                               int |
                                               List[Dict[str, str]]]]
                     ) -> None:
    """Pickle (save to file) the OMDB records, both the raw and the
    shortened datasets."""

    with open('C:/Users/maxru/eclipse-workspace/movie_list_dvlp/'
              'movie_list_parsing/pickled_OMDB_dicts.data',
              'wb') as f:
        pickle.dump(all_omdb_dicts, f)

    with open('C:/Users/maxru/eclipse-workspace/movie_list_dvlp/'
              'movie_list_parsing/pickled_OMDBs_abrvd.data',
              'wb') as f:
        pickle.dump(all_omdb_abrvd, f)


def pull_omdb_records(cursor: pymysql.cursors.Cursor
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
    pickle_omdb_recs(omdb_data_raw, omdb_data)

    # Return both lists, of the complete OMDB records and the shortened
    # ones.
    return omdb_data_raw, omdb_data


def get_omdb_data(method: str,
                  cursor: pymysql.cursors.Cursor = None,
                  raw: bool = False
                  ) -> List[List[Dict[str, str | int]]] | \
                       List[List[str | int | List[Dict[str, str]]]] | \
                       None:
    valid_methods = ['load from file', 'request from OMDB']

    # Raise error if specified method of data retrieval isn't covered.
    if method not in valid_methods:
        print("ERROR: entry for 'method' parameter not valid. Please"
              "enter one of the following instead: ")
        for valid_method in valid_methods:
            print(valid_method)
        return

    else:
        # When loading/unpickling OMDB data from file.
        if method == 'load from file':
            if not raw:
                return unpickle_stored_omdb_recs()[1]
            else:
                return unpickle_stored_omdb_recs()[0]
        elif method == 'request from OMDB':
            if not cursor:
                print("ERROR: get_omdb_data() needs a pymysql cursor"
                      "in order to get OMDB records via method 'request"
                      "from OMDB'")
            else:
                if not raw:
                    return pull_omdb_records(cursor)[1]
                else:
                    return pull_omdb_records(cursor)[0]


def prepare_data_ratings(omdb_data: List[List[str |
                                              int |
                                              List[Dict[str, str]]]]
                         ) -> List[List[int | str | float]]:
    """Create a 2D list of data on the movies' various review scores
    in OMDB. (OMDB features IMDb, Rotten Tomatoes, and MetaCritic
    scores.) The scores are here transformed to decimals."""

    copied_omdb_data = copy.deepcopy(omdb_data)

    ratings_data = []

    for i in copied_omdb_data:
        curr_rec = [i[0], i[1], i[2], None, None, None]
        for rev_dict in i[9]:
            if rev_dict['Source'] == 'Internet Movie Database':
                mc_rating = rev_dict['Value']
                mc_rating = mc_rating.split('/')[0]
                mc_rating = round((float(mc_rating) / 10), 2)
                curr_rec[3] = mc_rating

            elif rev_dict['Source'] == 'Rotten Tomatoes':
                rt_rating = rev_dict['Value']
                rt_rating = rt_rating.replace('%', '')
                rt_rating = round((float(rt_rating) / 100), 2)
                curr_rec[4] = rt_rating

            elif rev_dict['Source'] == 'Metacritic':
                mc_rating = rev_dict['Value']
                mc_rating = mc_rating.split('/')[0]
                mc_rating = round((float(mc_rating) / 100), 2)
                curr_rec[5] = mc_rating

        ratings_data.append(curr_rec)

    return ratings_data


def gnr8_table_critic_ratings(cursor: pymysql.cursors.Cursor,
                              ratings_data: List[List[int | str
                                                      | float]]
                              ) -> None:
    """Creates the 'critic_ratings' table (from square one) using the
    ratings data prepared by the prepare_data_ratings() method."""

    # Drop the existing critic_ratings table in the MySQL db.
    cursor.execute("DROP TABLE IF EXISTS critic_ratings")

    # Construct the 'CREATE TABLE' SQL statement
    create_table_str = "CREATE TABLE IF NOT EXISTS critic_ratings("
    ratings_data_col_names = ['Movie_ID', 'Title', 'Year', 'IMDB_Score',
                              'RT_Score', 'MetaC_Score']
    num_cols = len(ratings_data_col_names)
    for i in range(num_cols):
        curr_attr = ratings_data_col_names[i]
        var_type = " varchar(80)"

        if "Score" in curr_attr:
            var_type = " float"
        elif "Movie_ID" in curr_attr:
            var_type = " int NOT NULL"

        create_table_str += curr_attr + var_type + ', '
    create_table_str += 'FOREIGN KEY(Movie_ID) REFERENCES ' \
                        'allmovies(Movie_ID))'
    # create_table_str += 'PRIMARY KEY(Movie_ID) )'
    # print(create_table_str)

    # Execute the 'CREATE TABLE' statement
    cursor.execute(create_table_str)

    # Insert the movie ratings records into this new critic_ratings
    # table.
    cursor.executemany("INSERT INTO critic_ratings VALUES (%s, %s, %s,"
                       " %s, %s, %s)", ratings_data)


def prepare_data_genre(omdb_data: List[List[str |
                                            int |
                                            List[Dict[str, str]]]]
                       ) -> List[List[int | str]]:
    """Returns a 2D list of data on the movies' various genres, as
    listed in OMDB, given the abbreviated OMDB data. A list of all
    genres is returned as well."""

    copied_omdb_data = copy.deepcopy(omdb_data)

    # Create a list of the unique genres featured in the data.
    unique_genres = []
    for i in copied_omdb_data:
        # Each OMDB movie record may show multiple genres, separated by
        # a comma.
        curr_genres = i[5].split(', ')
        for j in curr_genres:
            if j not in unique_genres:
                unique_genres.append(j)
    genre_count = len(unique_genres)

    # Create the eventual table's header by prepending a few attribute
    # names to the all_genres list.
    unique_genres = ["Movie_ID", "Title", "Year"] + unique_genres

    # With every genre now identified, create the genre data, where each
    # row represents a movie and its associated genres.
    prepped_genre_data = [unique_genres]
    for i in copied_omdb_data:
        curr_record = [i[0], i[1], i[2]] + ([0] * genre_count)
        curr_genres = i[5].split(', ')
        for j in curr_genres:
            gen_ind = unique_genres.index(j)
            curr_record[gen_ind] = 1
        prepped_genre_data.append(curr_record)

    return prepped_genre_data


def gnr8_table_genre(cursor: pymysql.cursors.Cursor,
                     prepped_data: List[List[int | str]]
                     ) -> None:
    """Creates the 'genres' table (from square one) using the
    genre data and list prepared by the prepare_data_genre() method."""

    # Drop the existing genre table in the MySQL db.
    cursor.execute("DROP TABLE IF EXISTS genres")

    # Construct the 'CREATE TABLE' SQL statement
    create_table_str = "CREATE TABLE IF NOT EXISTS genres("

    col_names = prepped_data.pop(0)

    num_cols = len(col_names)
    for i in range(num_cols):
        curr_attr = col_names[i].replace("-", "")
        var_type = " varchar(80)"

        if curr_attr not in ['Title', 'Year']:
            var_type = " int"

        create_table_str += curr_attr + var_type + ', '

    # Adding constraints as necessary
    constraint_strings = []
    # if "Movie_ID" in col_names:
    #     constraint_strings.append("PRIMARY KEY (Movie_ID)")
    if "Movie_ID" in col_names:
        constraint_strings.append("FOREIGN KEY(Movie_ID) REFERENCES "
                                  "allmovies(Movie_ID)")
    for attr in col_names:
        attr = attr.replace("-", "")
        if attr not in ["Movie_ID", "Title", "Year"]:
            constraint_strings.append("CHECK (" + attr + " in (0, 1))")

    if len(constraint_strings) > 0:
        total_constraint_str = ", ".join(constraint_strings)
        total_constraint_str = total_constraint_str + ")"
        create_table_str = create_table_str + total_constraint_str

    # Execute the 'CREATE TABLE' statement
    cursor.execute(create_table_str)

    # Create and execute the 'INSERT' statements
    value_rpl_str = "(" + ", ".join(["%s"] * num_cols) + ")"
    cursor.executemany("INSERT INTO genres VALUES " +
                       value_rpl_str,
                       prepped_data)


def prepare_data_omdb(omdb_data: List[List[str |
                                           int |
                                           List[Dict[str, str]]]]
                      ) -> List[List[int | str | float | None]]:
    """Returns a 2D list of preprocessed, reduced data from OMDB, given
    the unprocessed, reduced OMDB data.
    This involves parsing the original's list of dictionaries of
    reviews into several float-type fields; transforming the box office
    earnings field from a string to an integer; and doing the same for
    the runtime field."""

    copied_omdb_data = copy.deepcopy(omdb_data)

    for i in copied_omdb_data:
        # Parse list of dicts for review scores.
        curr_rev_dict = i[9]
        imdb_score, rt_score, mc_score = None, None, None
        for j in curr_rev_dict:
            if j['Source'] == "Internet Movie Database":
                imdb_score = j['Value']
                imdb_score = imdb_score.split('/')[0]
                imdb_score = round((float(imdb_score) / 10), 2)
            elif j['Source'] == "Rotten Tomatoes":
                rt_score = j['Value']
                rt_score = rt_score.replace('%', '')
                rt_score = round((float(rt_score) / 100), 2)
            elif j['Source'] == "Metacritic":
                mc_score = j['Value']
                mc_score = mc_score.split('/')[0]
                mc_score = round((float(mc_score) / 100), 2)

        i[9] = imdb_score
        i.insert(10, rt_score)
        i.insert(11, mc_score)

        # Transform BoxOffice earnings attribute to int
        curr_earnings = i[12]
        # print(i)
        # print(curr_earnings)
        if curr_earnings in ['N/A', 0]:
            i[12] = None
        else:
            i[12] = int(curr_earnings.replace("$", "").replace(",", ""))
        # print(i[11])

        # Transform runtime to int. NOTE: 'N/A' values in this runtime
        # field can result in an error, but these are helpful because
        # they seem to indicate that an incorrect record was pulled in
        # the OMDB request.
        i[4] = int(i[4].replace(" min", ""))

    return copied_omdb_data


def gnr8_table_omdb(cursor: pymysql.cursors.Cursor,
                    omdb_data: List[List[int | str | float]]
                    ) -> None:
    """Creates the 'omdb' table (from square one) using the
    abbreviated/reduced OMDB data prepared by the
    prepare_data_omdb() method."""

    # Drop the existing 'omdb' table in the MySQL db.
    cursor.execute("DROP TABLE IF EXISTS omdb")

    # Construct the 'CREATE TABLE' SQL statement.
    create_table_str = "CREATE TABLE IF NOT EXISTS omdb("

    col_names = ['Movie_ID', 'Title', 'Year', 'OMDB_Release', 'Runtime',
                 'Genres', 'Directors', 'Writers', 'Actors',
                 'IMDB_Score', 'RT_Score', 'MetaC_Score', 'Earnings']
    num_cols = len(col_names)

    for i in range(num_cols):
        curr_attr = col_names[i]
        var_type = " varchar(80)"

        if curr_attr in ['Movie_ID', 'Runtime', 'Earnings']:
            var_type = ' int'

        if "Score" in curr_attr:
            var_type = " float"

        create_table_str += curr_attr + var_type + ', '
    create_table_str += ' PRIMARY KEY(Movie_ID))'

    # Execute the 'CREATE TABLE' statement.
    cursor.execute(create_table_str)

    # Create and execute the 'INSERT' statements.
    arg_string = '(' + ", ".join(['%s'] * num_cols) + ')'
    cursor.executemany("INSERT INTO omdb VALUES " + arg_string,
                       omdb_data)


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
        prepped_omdb_data = prepare_data_omdb(omdb_data)
        gnr8_table_omdb(cursor, prepped_omdb_data)
        prepped_genre_data = prepare_data_genre(omdb_data)
        gnr8_table_genre(cursor, prepped_genre_data)
        prepped_ratings_data = prepare_data_ratings(omdb_data)
        gnr8_table_critic_ratings(cursor, prepped_ratings_data)
    elif table_name == 'omdb':
        prepped_omdb_data = prepare_data_omdb(omdb_data)
        gnr8_table_omdb(cursor, prepped_omdb_data)
    elif table_name == 'genre':
        prepped_genre_data = prepare_data_genre(omdb_data)
        gnr8_table_genre(cursor, prepped_genre_data)
    elif table_name == 'critic_ratings':
        prepped_ratings_data = prepare_data_ratings(omdb_data)
        gnr8_table_critic_ratings(cursor, prepped_ratings_data)


def compare_keys_btwn_new_and_loaded(cursor: pymysql.cursors.Cursor,
                                     loaded_data: List[
                                         List[
                                             str |
                                             int |
                                             List[Dict[str, str]]
                                         ]]
                                     ) -> None:
    query_all_titles = "SELECT Movie_ID, Title, Year FROM allMovies"
    cursor.execute(query_all_titles)

    allmovies_dict = {}
    for (movie_id, title, year) in cursor:
        title_and_year = ' '.join([title, year])
        if movie_id not in allmovies_dict:
            allmovies_dict[movie_id] = title_and_year
        else:
            if allmovies_dict[movie_id] != title_and_year:
                raise Exception(f'ERROR DURING OMDB PROCESS: Duplicate '
                                f'key among records that don\'t share '
                                f'title and year: \n'
                                f'\n'
                                f'Key = {movie_id}\n'
                                f'Preexisting title and year: \t'
                                f'{allmovies_dict[movie_id]}\n'
                                f'New title and year: \t\t'
                                f'{title_and_year}')

    omdb_dict = {}
    for i in loaded_data:
        movie_id = i[0]
        title_and_year = ' '.join([i[1], i[2]])
        if movie_id not in omdb_dict:
            omdb_dict[movie_id] = title_and_year
        else:
            if omdb_dict[movie_id] != title_and_year:
                raise Exception(f'ERROR DURING OMDB PROCESS: Duplicate '
                                f'keys among differing "omdb_dict"'
                                f' records: \n'
                                f'\n'
                                f'Key = {movie_id}\n'
                                f'Preexisting title and year: \t'
                                f'{omdb_dict[movie_id]}\n'
                                f'New title and year: \t\t'
                                f'{title_and_year}')

    for movie_id in allmovies_dict:
        if allmovies_dict[movie_id] != omdb_dict[movie_id]:
            raise Exception(f'ERROR DURING OMDB PROCESS: DISCREPANCY IN '
                            f'KEYS between \'allmovies\' MySQL table '
                            f'and the loaded omdb data. \n'
                            f'\n'
                            f'Key: {movie_id}\n'
                            f'Preexisting title and year:\t\t'
                            f'{omdb_dict[movie_id]}\n'
                            f'New title and year:\t\t\t\t'
                            f'{allmovies_dict[movie_id]}\n'
                            f'\n'
                            f'RECOMMENDED ACTION: For the '
                            f'create_omdb_tables method, change '
                            f'omdb_load_method parameter to \'request '
                            f'from OMDB\'')


def create_omdb_tables(omdb_load_method: str,
                       db: pymysql.connections.Connection,
                       which_table: str = 'all',
                       omdb_as_dicts: bool=False
                       ) -> None:
    """Gets OMDB data for the movies in the 'allmovies' MySQL table,
    then creates the OMDB-related tables in that same db. (These include
    'omdb', 'genres', and 'critic_ratings'.)"""

    # Create a cursor from the db.
    cursor = db.cursor()

    # Read in the OMDB data, largely unprocessed, by requesting through
    # their API or by loading from file the previous requests.
    omdb_records = get_omdb_data(omdb_load_method, cursor,
                                 raw=omdb_as_dicts)

    # Check for discrepancies between unpickled OMDB data and allmovies
    # table (from MySQL.)
    if not omdb_as_dicts:
        compare_keys_btwn_new_and_loaded(cursor, omdb_records)

    # Create the OMDB-related tables in the MySQL db. At time of writing
    # these include 'omdb', 'genres', and 'critic_ratings'. Create all
    # these by specifying 'all'.
    gnr8_table_from_omdb_data(which_table, cursor, omdb_records)

    # Commit the changes to the db.
    db.commit()
