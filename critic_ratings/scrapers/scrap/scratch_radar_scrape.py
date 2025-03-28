import pandas as pd
import pickle
import os

from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup






# # Start the dictionary of this film's details.

# searched_title = 'Secret Mall Apartamento'
# searched_year = '2025'
# searched_director = 'Max Webster'
# link_retrieved = '/movie/secret-mall-apartamento'


# # Set up the Selenium Chromium driver
# options = webdriver.ChromeOptions()
# options.add_argument('--ignore-certificate-errors')
# options.add_argument('--ignore-ssl-errors')
# options.page_load_strategy = 'eager'
# driver = webdriver.Chrome(options)
# driver.implicitly_wait(5)

# # Navigate to the film's main page (on Metacritic.)
# driver.get('https://www.metacritic.com/movie/secret-mall-apartment/')
# soup = BeautifulSoup(driver.page_source, 'html.parser')

# ### FINDING AND ADDING FILM DETAILS FROM THE METACRITIC PAGE

# # Title (retrieved)
# title = None
# title_element = soup.select_one('div.c-productHero_title')
# if title_element:
#     title = title_element.text.strip()
#     # detail_dict['Title'] = title
#     print(title, end='\t')

# # Year (retrieved)
# year = None
# metadata_header_elem = soup.select_one('div.c-heroMetadata')
# if metadata_header_elem:
#     year_element = metadata_header_elem.select_one('li.c-heroMetadata_item')
#     year = year_element.text.strip()
#     # detail_dict['Year'] = year
#     print(year)

# # Metascore
# metascore = None
# review_score_elems = soup.select('div.c-productScoreInfo.u-clearfix')
# for elem in review_score_elems:
#     review_type = elem.get('data-testid')
#     if review_type == 'critic-score-info':
#         metascore = elem.select_one('div.c-siteReviewScore').text.strip()
#         if metascore == 'tbd':
#             metascore = None
#         else:
#             metascore = float(metascore) / 100
#         # detail_dict['Metascore'] = metascore
#         # print(film_title, 'Metascore:', metascore)

# # Summary
# summary = None
# summary_element = soup.select_one('span.c-productDetails_description.g-text-xsmall')
# if summary_element:
#     summary = summary_element.text.strip()
#     # detail_dict['Summary'] = summary
#     # print(film_title, summary)

# # Director(s)
# directors = None
# directors_detail_element = soup.select_one('div.c-crewList.g-inner-spacing-bottom-small.c-productDetails_staff_directors')
# if directors_detail_element:
#     directors_entries_element = directors_detail_element.select('a.c-crewList_link.u-text-underline')
#     directors = ' '.join([director.text.strip() for director in directors_entries_element])
#     # detail_dict['Directors'] = directors
#     # print(film_title, directors_str)

# # Writer(s)
# writers = None
# writers_detail_element = soup.select_one('div.c-crewList.g-inner-spacing-bottom-small.c-productDetails_staff_writers')
# # writers_element = soup.select_one('div.c-crewList.g-inner-spacing-bottom-small.c-productDetails_staff_writers').select('a.c-crewList_link.u-text-underline')
# if writers_detail_element:
#     writer_entries_element = writers_detail_element.select('a.c-crewList_link.u-text-underline')
#     writers = ' '.join([writer.text.strip() for writer in writer_entries_element])
#     # detail_dict['Writers'] = writers
#     # print(film_title, writers_str)


# # Runtime and (US theatrical) release date
# runtime_in_minutes = None
# release_date = None
# prod_detail_elems = soup.select('div.c-movieDetails_sectionContainer')
# for elem in prod_detail_elems:
#     prod_detail_type = elem.select_one('span.g-text-bold').text.strip()

#     if prod_detail_type == 'Duration':
#         runtime_str = elem.select_one('span.g-outer-spacing-left-medium-fluid').text.strip()
    
#         # print(film_title, film_year, runtime_str,
#         #     sep='\t', end='\n\n')
        
#         if 'h' not in runtime_str:
#             runtime_str = '0 h ' + runtime_str
#         if 'm' not in runtime_str:
#             runtime_str = runtime_str + ' 0 m'
        
#         runtime_str = runtime_str.replace('h', '').replace('m', '')
#         runtime_hrs, runtime_mins = [int(i) for i in runtime_str.split()]
#         runtime_in_minutes = runtime_hrs * 60 + runtime_mins

#         # detail_dict['Runtime'] = runtime_in_minutes
#         # print(film_title, runtime_in_minutes)

#     if prod_detail_type == 'Release Date':
#         release_date = elem.select_one('span.g-outer-spacing-left-medium-fluid').text.strip()
#         release_date = datetime.strptime(release_date, '%b %d, %Y')
#         release_date = datetime.strftime(release_date, '%Y-%m-%d')
#         # detail_dict['Release Date'] = release_date
#         # print(film_title, release_date)

# detail_dict = {
#     'Title Searched': searched_title,
#     'Year Searched': searched_year,
#     'Director Searched': searched_director,
#     'Link Retrieved': link_retrieved,
#     'Title Result': title,
#     'Year Result': year,
#     'Director Result': directors,
#     'Metascore': metascore,
#     'Runtime': runtime_in_minutes,
#     'Summary': summary,
#     'Writers': writers,
# }

# Close the driver
driver.quit()
# list_of_info_dicts.append(detail_dict)


# def parse_show_name(show_name: str,
#                         ) -> str:
#         """Parse a Siskel show's title into those of the series and film,
#         which sometimes comprise it.
        
#         An auxiliary method of the siskel_scrape."""

#         film_title = None
#         series_prepends = None


#         if ': ' in show_name:
#             parsed_show_name = show_name.split(': ')

#             # In the event that the film title contains a single
#             # colon, detect and combine its erroneously split 
#             # segments.
#             if len(parsed_show_name) >= 2:
#                 potential_title_segment = parsed_show_name[-2]

#                 some_valid_series_names = ['OFF CENTER', 
#                                         'ARTHUR ERICKSON',
#                                         'ADFF',
#                                         ]

#                 if potential_title_segment not in some_valid_series_names and \
#                 not any(char.islower() for char in potential_title_segment):
#                     film_title = ': '.join(parsed_show_name[-2:])
#                     series_prepends = parsed_show_name[:-2]
#                 else:
#                     film_title = parsed_show_name[-1]
#                     series_prepends = parsed_show_name[:-1]
#         else:
#             film_title = show_name
#             series_prepends = None

#         return film_title, series_prepends


# siskel_sup_info_dict = None
# with open('data/pkl/siskel/siskel_show_info_dict.pkl', 'rb') as file:
#     siskel_sup_info_dict = pickle.load(file)

# # print(siskel_sup_info_dict.keys())
# # print(siskel_sup_info_dict.get('DR. STRANGELOVE'))

# for show_name in siskel_sup_info_dict.keys():
#      print(show_name, '\t\t', parse_show_name(show_name)[0])


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
