import urllib.parse

import mysql.connector
import requests as requests
import pickle


def load_stored_OMDB_recs():
    with open('C:/Users/maxru/eclipse-workspace/movie_list_dvlp/movie_list_parsing/pickled_OMDB_dicts.data', 'rb') as f:
        all_OMDB_dicts = pickle.load(f)

    with open('C:/Users/maxru/eclipse-workspace/movie_list_dvlp/movie_list_parsing/pickled_OMDBs_abrvd.data',
              'rb') as f:
        all_OMDB_abrvd = pickle.load(f)

    return all_OMDB_dicts, all_OMDB_abrvd


def pickle_OMDB_recs(all_OMDB_dicts, all_OMDB_abrvd):
    with open('C:/Users/maxru/eclipse-workspace/movie_list_dvlp/movie_list_parsing/pickled_OMDB_dicts.data', 'wb') as f:
        pickle.dump(all_OMDB_dicts, f)

    with open('C:/Users/maxru/eclipse-workspace/movie_list_dvlp/movie_list_parsing/pickled_OMDBs_abrvd.data',
              'wb') as f:
        pickle.dump(all_OMDB_abrvd, f)


def pull_OMDB_records(aCursor):
    all_OMDB_dicts = []
    all_OMDB_abrvd = []

    keyFile = "C:/Users/maxru/Programming/Python/.secret/OMDB_API.txt"

    with open(keyFile) as f:
        API_key = f.read()

    query_all_titles = "SELECT Title, Year FROM allMovies"
    aCursor.execute(query_all_titles)

    titles_years_list = []

    erroneous_OMDB_pulls = []

    for (Title, Year) in aCursor:
        titles_years_list.append((Title, Year))
        # print("{}   |   {}".format(Title, Year))

        curr_title = urllib.parse.quote_plus(Title)

        # Lydia Tar needs special treatment for her HTML request
        if curr_title == 'T%C3%83%C2%A1r':
            curr_title = 'T%C3%A1r'

        curr_year = str(Year)

        OMDB_entry = requests.get('http://www.omdbapi.com/?i=tt3896198&apikey=' + API_key
                                  + '&t=' + curr_title + '&y=' + str(curr_year)).json()

        if OMDB_entry['Response'] == 'False':
            erroneous_OMDB_pulls.append((curr_title, curr_year))
            continue

        all_OMDB_dicts.append(OMDB_entry)

        OMDB_entry_list = [OMDB_entry['Title'], OMDB_entry['Year'],
                           OMDB_entry['Released'], OMDB_entry['Runtime'],
                           OMDB_entry['Genre'], OMDB_entry['Director'],
                           OMDB_entry['Writer'], OMDB_entry['Actors'],
                           OMDB_entry['Ratings'],
                           OMDB_entry.get('BoxOffice', 0)]
        # print(OMDB_entry_list)
        all_OMDB_abrvd.append(OMDB_entry_list)

    if erroneous_OMDB_pulls:
        print("FUCKED UP REQUESTS:\n")
        for i in erroneous_OMDB_pulls:
            print(i)

    pickle_OMDB_recs(all_OMDB_dicts, all_OMDB_abrvd)

    return all_OMDB_dicts, all_OMDB_abrvd


def create_2D_ratings_data(all_OMDB_abrvd):
    ratings_data = []

    for i in all_OMDB_abrvd:
        curr_rec = [i[0], i[1], None, None, None]
        for rev_dict in i[8]:
            if rev_dict['Source'] == 'Internet Movie Database':
                mc_rating = rev_dict['Value']
                mc_rating = mc_rating.split('/')[0]
                mc_rating = round((float(mc_rating) / 10), 2)
                # print(rev_dict['Value'], imdb_rating, sep='\t')
                curr_rec[2] = mc_rating

            elif rev_dict['Source'] == 'Rotten Tomatoes':
                rt_rating = rev_dict['Value']
                rt_rating = rt_rating.replace('%', '')
                rt_rating = round((float(rt_rating) / 100), 2)
                # print(rt_rating, rev_dict['Value'], sep='\t')
                curr_rec[3] = rt_rating

            elif rev_dict['Source'] == 'Metacritic':
                mc_rating = rev_dict['Value']
                mc_rating = mc_rating.split('/')[0]
                mc_rating = round((float(mc_rating) / 100), 2)
                # print(rev_dict['Value'], mc_rating, sep='\t')
                curr_rec[4] = mc_rating

        ratings_data.append(curr_rec)

    return ratings_data


def gnr8_new_ratings_table(aCursor, ratings_data):

    aCursor.execute("DROP TABLE IF EXISTS critic_ratings")

    create_table_str = "CREATE TABLE IF NOT EXISTS critic_ratings("

    ratings_data_col_names = ['Title', 'Year', 'IMDB_Score', 'RT_Score', 'MetaC_Score']
    num_cols = len(ratings_data_col_names)
    for i in range(num_cols):
        curr_attr = ratings_data_col_names[i]
        var_type = " varchar(80)"

        if "Score" in curr_attr:
            var_type = " float"

        if i < num_cols - 1:
            create_table_str += curr_attr + var_type + ', '
        else:
            create_table_str += curr_attr + var_type + ')'

    aCursor.execute(create_table_str)
    aCursor.executemany("INSERT INTO critic_ratings VALUES (%s, %s, %s, %s, %s)", ratings_data)


def gnr8_genre_2d_data(omdb_recs_abrvd):
    all_genres = []
    for i in omdb_recs_abrvd:
        curr_genres = i[4].split(', ')
        for j in curr_genres:
            if j not in all_genres:
                all_genres.append(j)
    num_genres = len(all_genres)
    all_genres = ["Title", "Year"] + all_genres
    # print(all_genres)

    genre_data = []
    for i in omdb_recs_abrvd:
        curr_record = [i[0], i[1]] + ([0] * num_genres)
        curr_genres = i[4].split(', ')
        # print(i[0], curr_genres)
        for j in curr_genres:
            gen_ind = all_genres.index(j)
            curr_record[gen_ind] = 1
        # print(curr_record, "\t" + str(len(curr_record)))
        genre_data.append(curr_record)

    return all_genres, genre_data


def gnr8_genre_table(table_name, col_names, aCursor, the_data):

    aCursor.execute("DROP TABLE IF EXISTS " + table_name)

    create_table_str = "CREATE TABLE IF NOT EXISTS " + table_name + "("

    num_cols = len(col_names)
    for i in range(num_cols):
        curr_attr = col_names[i].replace("-", "")
        var_type = " varchar(80)"

        if curr_attr not in ['Title', 'Year']:
            var_type = " int"

        if i < num_cols - 1:
            create_table_str += curr_attr + var_type + ', '
        else:
            create_table_str += curr_attr + var_type + ')'

    # Adding constraints as necessary
    constraint_strings = []
    if "Title" in col_names and "Year" in col_names:
        constraint_strings.append("PRIMARY KEY (Title, Year)")
    for attr in col_names:
        attr = attr.replace("-", "")
        if attr not in ["Title", "Year"]:
            constraint_strings.append("CHECK (" + attr + " in (0, 1))")

    if len(constraint_strings) > 0:
        total_constraint_str = ", ".join(constraint_strings)
        total_constraint_str = total_constraint_str + ")"
        create_table_str = create_table_str[:-1] + ", " + total_constraint_str

    # print(create_table_str)
    aCursor.execute(create_table_str)
    value_rpl_str = "(" + ", ".join(["%s"] * num_cols) + ")"
    aCursor.executemany("INSERT INTO " + table_name + " VALUES " + value_rpl_str, the_data)


def setup_omdb_abrvd_data(omdb_abrvd_raw):
    omdb_abrvd_processed = [ele[:] for ele in omdb_abrvd_raw]
    print(omdb_abrvd_processed[0])
    # counter = 0
    for i in omdb_abrvd_processed:

        # Review scores
        curr_rev_dict = i[8]
        IMDB_score, RT_score, MC_score = None, None, None
        for j in curr_rev_dict:
            if j['Source'] == "Internet Movie Database":
                IMDB_score = j['Value']
                IMDB_score = IMDB_score.split('/')[0]
                IMDB_score = round((float(IMDB_score) / 10), 2)
            elif j['Source'] == "Rotten Tomatoes":
                RT_score = j['Value']
                RT_score = RT_score.replace('%', '')
                RT_score = round((float(RT_score) / 100), 2)
            elif j['Source'] == "Metacritic":
                MC_score = j['Value']
                MC_score = MC_score.split('/')[0]
                MC_score = round((float(MC_score) / 100), 2)

        i[8] = MC_score
        i.insert(8, RT_score)
        i.insert(8, IMDB_score)

        # Transform BoxOffice earnings attribute to int
        curr_earnings = i[11]
        # print(i)
        # print(curr_earnings)
        if curr_earnings in ['N/A', 0]:
            i[11] = None
        else:
            i[11] = int(curr_earnings.replace("$", "").replace(",", ""))
        # print(i[10])

        # Transform runtime to int. NOTE: 'N/A' values in this field can
        # will result in an error, but these are helpful because they
        # seem to indicate that an incorrect record was pulled in the
        # OMDB request.
        i[3] = int(i[3].replace(" min", ""))

        # counter += 1
        # if counter <= 19:
        #     print(i)
    # print(omdb_abrvd_processed[:10])
    return omdb_abrvd_processed


def gnr8_omdb_abrvd_table(aCursor, omdb_abrvd_data):
    table_name = 'omdb_abrvd'
    aCursor.execute("DROP TABLE IF EXISTS " + table_name)

    create_table_str = "CREATE TABLE IF NOT EXISTS " + table_name + "("

    print(omdb_abrvd_data[0])
    print(len(omdb_abrvd_data[0]))
    col_names = ['Title', 'Year', 'OMDB_Release', 'Runtime',
                 'Genres', 'Directors', 'Writers', 'Actors',
                 'IMDB_Score', 'RT_Score', 'MetaC_Score', 'Earnings']
    num_cols = len(col_names)
    for i in range(num_cols):
        curr_attr = col_names[i]
        var_type = " varchar(80)"

        if curr_attr in ['Runtime', 'Earnings']:
            var_type = ' int'

        if "Score" in curr_attr:
            var_type = " float"

        create_table_str += curr_attr + var_type + ', '

    create_table_str += ' PRIMARY KEY(Title, Year))'
    aCursor.execute(create_table_str)
    print(num_cols)
    print(", ".join(['%s'] * num_cols))
    arg_string = '(' + ", ".join(['%s'] * num_cols) + ')'
    aCursor.executemany("INSERT INTO " + table_name + " VALUES " + arg_string, omdb_abrvd_data)


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yos",
    database="movieDB"
)

aCursor = mydb.cursor()

# all_OMDB_dicts, omdb_recs_abrvd = pull_OMDB_records(aCursor)
all_OMDB_dicts, omdb_recs_abrvd = load_stored_OMDB_recs()

omdb_recs_processed = setup_omdb_abrvd_data(omdb_recs_abrvd)
gnr8_omdb_abrvd_table(aCursor, omdb_recs_processed)

all_genres, genre_data = gnr8_genre_2d_data(omdb_recs_abrvd)
gnr8_genre_table("allMovsGenres", all_genres, aCursor, genre_data)

rev_records = create_2D_ratings_data(omdb_recs_abrvd)
gnr8_new_ratings_table(aCursor, rev_records)
mydb.commit()
aCursor.close()
mydb.close()
