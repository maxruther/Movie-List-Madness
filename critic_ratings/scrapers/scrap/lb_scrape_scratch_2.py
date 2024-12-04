import pandas as pd
import re





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
