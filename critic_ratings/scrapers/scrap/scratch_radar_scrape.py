import pandas as pd
import pickle
import os


def parse_show_name(show_name: str,
                        ) -> str:
        """Parse a Siskel show's title into those of the series and film,
        which sometimes comprise it.
        
        An auxiliary method of the siskel_scrape."""

        film_title = None
        series_prepends = None


        if ': ' in show_name:
            parsed_show_name = show_name.split(': ')

            # In the event that the film title contains a single
            # colon, detect and combine its erroneously split 
            # segments.
            if len(parsed_show_name) >= 2:
                potential_title_segment = parsed_show_name[-2]

                some_valid_series_names = ['OFF CENTER', 
                                        'ARTHUR ERICKSON',
                                        'ADFF',
                                        ]

                if potential_title_segment not in some_valid_series_names and \
                not any(char.islower() for char in potential_title_segment):
                    film_title = ': '.join(parsed_show_name[-2:])
                    series_prepends = parsed_show_name[:-2]
                else:
                    film_title = parsed_show_name[-1]
                    series_prepends = parsed_show_name[:-1]
        else:
            film_title = show_name
            series_prepends = None

        return film_title, series_prepends


siskel_sup_info_dict = None
with open('data/pkl/siskel/siskel_show_info_dict.pkl', 'rb') as file:
    siskel_sup_info_dict = pickle.load(file)

# print(siskel_sup_info_dict.keys())
# print(siskel_sup_info_dict.get('DR. STRANGELOVE'))

for show_name in siskel_sup_info_dict.keys():
     print(show_name, '\t\t', parse_show_name(show_name)[0])


# mb_showtimes = None
# with open('data/pkl/musicbox/musicbox_showtimes_dict.pkl', 'rb') as file:
#     mb_showtimes = pickle.load(file)

# new_dict = {}
# for movie in list(mb_showtimes.keys())[:5]:
#     new_dict[movie] = mb_showtimes[movie]
# print(new_dict, '\n\n')

# df1 = pd.DataFrame.from_dict(new_dict, orient='index')
# df_stacked = df1.stack().reset_index()
# df_stacked.columns = ['Movie', 'Showtime_Index', 'Showtime']
# df_stacked = df_stacked[['Movie', 'Showtime']]
# print(df_stacked)

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
