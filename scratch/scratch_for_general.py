import typing

import pandas as pd
import pymysql

mydb = pymysql.connect(
    host="localhost",
    user="root",
    password="yos",
    database="movieDB"
)

cursor = mydb.cursor()



reviewer_vars = {
    'ebert': {'mysql_review_fld_name': 'Ebert_Score',
              'mapping_varname_suffix': 'ebert'},
    'metacritic': {'mysql_review_fld_name': 'MC_Score',
                   'mapping_varname_suffix': 'metacritic'},
    'rotten tomatoes': {'mysql_review_fld_name': 'MC_Score',
                        'mapping_varname_suffix': 'metacritic'},
}

for i in reviewer_vars:
    print(list(reviewer_vars[i].values()))





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