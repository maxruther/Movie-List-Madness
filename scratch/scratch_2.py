import datetime
import re
import pickle


mb_showtime_dict = None
with open('musicbox_films_showtimes_dict.pkl', 'rb') as file:
    mb_showtime_dict = pickle.load(file)

mb_film_details_dict = None
with open('musicbox_film_details_dict.pkl', 'rb') as file:
    mb_film_details_dict = pickle.load(file)

for pair in mb_showtime_dict.items():
    print(pair)

print(mb_film_details_dict['Legend'])

for showtime in mb_showtime_dict['Legend']:
    movie_runtime = mb_film_details_dict['Legend']['Runtime']
    runtime_delta = datetime.timedelta(minutes=movie_runtime)
    movie_start_str = showtime.strftime('%Y-%m-%dT%H:%M:%S')
    movie_end = showtime + runtime_delta
    movie_end_str = movie_end.strftime('%Y-%m-%dT%H:%M:%S')
    print('Legend', movie_runtime, movie_start_str, movie_end_str, sep='\n')

test_string_calendar_datetime = "2025-01-21T09:00:00-06:00"

# tech_deet_list_test = ['2024', '132 mins', 'DCP']

# def tech_summary_list_to_dict(tech_summary_list: list[str],
#                               ) -> dict[str: int | str]:

#     tech_details = {}

#     year_pattern = r'^(\d{4})$'
#     runtime_pattern = r'^(\d*) mins?$'
#     format_pattern = r'(^DCP$|^\d\.\dmm$|^\d{1,3}mm$)'

#     for tech_detail in tech_summary_list:

#         year_match = re.search(year_pattern, tech_detail)
#         runtime_match = re.search(runtime_pattern, tech_detail)
#         format_match = re.search(format_pattern, tech_detail)

#         if year_match:
#             tech_details['Year'] = int(year_match.group(1))
#             # print(tech_details['Year'])
#             # print(type(tech_details['Year']))
#         elif runtime_match:
#             tech_details['Runtime'] = int(runtime_match.group(1))
#             # print(tech_details['Runtime'])
#             # print(type(tech_details['Runtime']))
#         elif format_match:
#             tech_details['Format'] = format_match.group(1)
#             # print(tech_details['Format'])
#             # print(type(tech_details['Format']))

#     return tech_details


# print(tech_summary_list_to_dict(tech_deet_list_test))


# pattern = r'(.*)\ \((\d{4})\)$'
# test_str = 'Nosferatu (2024)'
# print(not not re.search(pattern, test_str))



# title = "Max Watches: STAR WARS: STARS WARRING ON"
# title = "Max Watches: Stars Wars Movies: Star Wars: STARS WARRING ON"
# title = "Max Watches: Stars Wars Movies: STAR WARS: STARS WARRING ON"
# title = 'The Worlds of Wiseman: HOSPITAL | 1970'

# if ': ' in title:
#     title_colon_split = title.split(': ')

#     # In the event that the film title contains a single
#     # colon, detect and combine its erroneously split 
#     # segments.
#     if len(title_colon_split) >= 2:
#         potential_title_segment = title_colon_split[-2]
#         if not any(char.islower() for char in potential_title_segment):
#             title = ': '.join(title_colon_split[-2:])
#             prepends = title_colon_split[:-2]
#         else:
#             title = title_colon_split[-1]
#             prepends = title_colon_split[:-1]
#     print(prepends, title)

# print('\n\n')
# print(': '.join(['National Theatre Live']))
# print(': '.join(['National Theatre Live', 'Arthur']))
# print('Barnacle Boy'.split(': '))



# my_string = 'Barnacle Boy'
# print(any(c.islower() for c in my_string))


# if not []:
#     print("Yeah, equivalent.")