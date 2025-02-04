import copy
from typing import List, Dict


def prep_omdb(omdb_data: List[List[str |
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
        try:
            i[4] = int(i[4].replace(" min", ""))
        except ValueError:
            raise Exception("\n\nInvalid or missing runtime retrieved " 
                            "from OMDb. Likely mismatch between the film's"
                            " title in OMDb and that of my movie list.\n"
                            f'OMDb Movie title:\t{i[1]}\n'
                            f'OMDb Release year:\t{i[2]}\n')

    return copied_omdb_data


def prep_genre(omdb_data: List[List[str |
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


def prep_ratings(omdb_data: List[List[str |
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
