import pandas as pd
import numpy as np
import re


print(not np.nan)



# test_str = """Dog Man,Dog Man,1.0,1.0,2025,2025,Peter Hastings,Peter Hastings,1.0,1.0,/movie/dog-man/
# Presence,Presence,1.0,1.0,2025,2024,Steven Soderbergh,Steven Soderbergh,1.0,1.0,/movie/presence/
# Sly Lives! (aka The Burden of Black Genius),Sly Lives! (aka the Burden of Black Genius),1.0,1.0,2025,2025,Questlove,Questlove,1.0,1.0,/movie/sly-lives!-aka-the-burden-of-black-genius/
# Rose,Rose,1.0,1.0,2025,2021,Aurélie Saada,Aurélie Saada,1.0,1.0,/movie/rose/"""

# print(test_str.split('\n'))

# for record in test_str.split('\n'):
#     # print(record.split(','))
#     print('\nINSERT INTO mc_searchresults\nVALUES (', ', '.join([f'"{x}"' for x in record.split(',')]), ');')





# # Reading in user prudentials from file, to obscure them to github.
# with open('C:/Users/maxru/eclipse-workspace/movie_list_dvlp/lb.txt', 'r') as file:
#     user, password = file.read().split()
#     # print(file.read().split())
#     print(user, password)


# # Parsing a film's title and year from a string that contains both (as featured in
# # Letterboxd pages dedicated tot hsoe films.)
# pattern = r'(^.+\S)\s+\((\d{4})\)$'
# text = 'Janet (Planet)   (2023)'
# title, year = re.search(pattern, text).groups()
# print(title, year, sep='\n')

# # Retrieving a list of link strings from a 'lb_diary_df', which now also features
# # title and year.
# user_url = 'yoyoyodaboy'
# lb_diary_df = pd.read_csv(f'{user_url}_lb_diary_df.csv')
# print(lb_diary_df['Letterboxd Link'].values)
