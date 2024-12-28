from typing import List, Dict

import pymysql


def test_for_movieid_discrepancies(cursor: pymysql.cursors.Cursor,
                                   loaded_data: List[
                                         List[
                                             str |
                                             int |
                                             List[Dict[str, str]]
                                         ]]
                                   ) -> None:
    
    # NOTE: If an OMDB record request fails, then this test will fail.

    query_all_titles = "SELECT Movie_ID, Title, Year FROM allMovies"
    cursor.execute(query_all_titles)

    allmovies_dict = {}
    for (movie_id, title, year) in cursor:

        # Store the concatenation of the movie's title and year, and
        # raise an exception if either are missing.
        try:
            title_and_year = ' '.join([title, year])
        except TypeError:
            raise Exception("\nMovie Title or Year probably missing from Evernote.\n"
                            f'Title:\t{title}\n'
                            f'Year:\t{year}\n')
        
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
        if movie_id not in omdb_dict:
            print(f'WARNING: Movie ID #{movie_id} not in OMDB data.\n',
                  f'(warning from test_for_movieid_discrepancies', 
                  f'method in omdb_builder.tests)\n')
            # print(f'{list(omdb_dict.items())}')
        else:
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
