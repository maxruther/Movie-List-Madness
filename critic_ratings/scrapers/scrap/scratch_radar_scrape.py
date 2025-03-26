import pandas as pd
import pickle
import os

mb_showtimes = None
with open('data/pkl/musicbox/musicbox_showtimes_dict.pkl', 'rb') as file:
    mb_showtimes = pickle.load(file)

new_dict = {}
for movie in list(mb_showtimes.keys())[:5]:
    new_dict[movie] = mb_showtimes[movie]
print(new_dict, '\n\n')

df1 = pd.DataFrame.from_dict(new_dict, orient='index')
df_stacked = df1.stack().reset_index()
df_stacked.columns = ['Movie', 'Showtime_Index', 'Showtime']
df_stacked = df_stacked[['Movie', 'Showtime']]
print(df_stacked)

# for movie, showtime_list in list(mb_showtimes.items())[:5]:
#                   print(movie)
#                   for showtime in showtime_list:
#                         print(f'\t{showtime}')
#                   print()




# test_str = 'data/pkl/siskel/siskel_inferior_show_info.pkl'
# test_str = 'data/pkl/barfy/siskel/siskel_inferior_show_info.pkl'

# test_str = test_str.replace('data/pkl/', '')
# print(test_str)
# parent_dir = test_str[:test_str.rfind('/')]
# print(parent_dir)
# filename = test_str[test_str.rfind('/')+1:]
# print(filename)
# # parent_dir, filename = test_str.split('/')
# # filename, _ = filename.split('.')
# # print(parent_dir, filename, sep='\n')

# print(os.path.dirname(test_str))

# filename_with_extension = os.path.basename(test_str)
# filename, extension = os.path.splitext(filename_with_extension)

# print(os.path.splitext(test_str))


# print(not 0.0)
# print(not int(0))



# test_radar_df = pd.read_csv('data/showtimes/test_radar.csv',
#                             dtype={
#                                 'Release Year': 'object',
#                                 'Runtime': 'object'
#                                 }
#                             )
# print(test_radar_df)
# print(test_radar_df.dtypes)

# test_radar_df.to_pickle('data/showtimes/test_radar.pkl')





# test_radar_dict = {
#     'Title': "THE IMPORTANCE OF BEING EARNEST",
#     'Release Year': 2025,
#     'Runtime': 180.0,
#     'Director': 'Max Webster',
# }



# with open('data/showtimes/test_radar.pkl', 'wb') as file:
#     pickle.dump(test_radar_dict, file)
