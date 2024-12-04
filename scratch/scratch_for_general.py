import typing

import pandas as pd
import pymysql

import re, string

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from fuzzywuzzy import fuzz


test = 0
if not test:
    print("Yep, 0's false")


# pattern = r'(^.+\S)\s+\((\d{4})\)$'
# text = 'Janet (Planet)   (2023)'
# title, year = re.search(pattern, text).groups()
# print(title, year, sep='\n')




# dictiony = {'barfy': 'fuck you'}
# print(list(dictiony.keys())[0])


# vectorizer = CountVectorizer()

# # str1 = "This is a sentence."
# # str2 = "This is another sentence."
# str1 = "tarot chicken"
# str2 = "tarot"

# vectors = vectorizer.fit_transform([str1, str2])
# similarity = cosine_similarity(vectors[0], vectors[1])
# print(similarity)
# similarity = fuzz.ratio(str1, str2)
# print(similarity)  # Output: 80

# print('TÁR'.lower())

# print(string.printable)
# pattern = re.compile('[^a-zA-Z0-9\s]*')
# pattern.sub('', "The Bird's Nest").lower().replace(' ', '%20')
# print(pattern.sub('', string.printable))
# print(pattern.sub('', "The Bird's Nest").lower().replace(' ', '%20') == 'the%20birds%20nest')

# mydb = pymysql.connect(
#     host="localhost",
#     user="root",
#     password="yos",
#     database="movieDB"
# )

# cursor = mydb.cursor()


# for i in []:
#     print("GO FUCK YOURSELF")


# print('\u2605')
# print('\u2605'.replace('\u2605', 'barfy'))
# print('\n\n')

# print('\u00BD')
# print('\u00BD'.replace('\u00BD','schlarfy'))



# reviewer_vars = {
#     'ebert': {'mysql_review_fld_name': 'Ebert_Score',
#               'mapping_varname_suffix': 'ebert'},
#     'metacritic': {'mysql_review_fld_name': 'MC_Score',
#                    'mapping_varname_suffix': 'metacritic'},
#     'rotten tomatoes': {'mysql_review_fld_name': 'MC_Score',
#                         'mapping_varname_suffix': 'metacritic'},
# }

# for i in reviewer_vars:
#     print(list(reviewer_vars[i].values()))





# def drop_table_stmt(k: int,
#                     data: list[list[str | list[str | int]]],
#                     ) -> str:
#     """Returns a "DROP TABLE IF EXISTS" statement for the MySQL db, given
#     the read-in Evernote data and the table's index therein."""
#     table_name = data[k][0][0]
#     drop_table_str = "DROP TABLE IF EXISTS " + table_name
#     # print(drop_table_str)
#     return drop_table_str


# a = pd.DataFrame().empty
# print(a)
#
# allmovies = []
#
# query_all_titles = "SELECT Movie_ID, Title, Year FROM allMovies"
# cursor.execute(query_all_titles)
#
# for record in cursor:
#     allmovies.append(list(record))
#
# print(allmovies[:3])




#
# allmovies_dict = {}
# for (movie_id, title, year) in cursor:
#     title_and_year = ' '.join([title, year])
#     if movie_id not in allmovies_dict:
#         allmovies_dict[movie_id] = title_and_year
#     else:
#         if allmovies_dict[movie_id] != title_and_year:
#             raise Exception(f'ERROR DURING OMDB PROCESS: Duplicate '
#                             f'key among records that don\'t share '
#                             f'title and year: \n'
#                             f'\n'
#                             f'Key = {movie_id}\n'
#                             f'Preexisting title and year: \t'
#                             f'{allmovies_dict[movie_id]}\n'
#                             f'New title and year: \t\t'
#                             f'{title_and_year}')