from selenium import webdriver

from scrapers.siskel_scrape import siskel_scrape
from scrapers.musicbox_scrape import musicbox_scrape

from schedulers.schedule_musicbox_shows import schedule_musicbox_shows
from schedulers.schedule_siskel_shows import schedule_siskel_shows

import pickle
import pandas as pd

import sys
sys.path.append('c:\\Users\\maxru\\eclipse-workspace\\movie_list_dvlp\\movie_list_parsing\\')
from critic_ratings.scrapers.old.mc_film_detail_scrape import mc_film_detail_scrape

# Set up the Selenium Chromium driver
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
driver = webdriver.Chrome(options)

# Load the showtimes and production info
with open('data/showtimes/siskel_films_showtimes_dict.pkl', 'rb') as file:
    showtime_dict_siskel = pickle.load(file)

with open('data/showtimes/siskel_films_details_dict.pkl', 'rb') as file:
    prod_info_dict_siskel = pickle.load(file)

with open('data/showtimes/musicbox_films_showtimes_dict.pkl', 'rb') as file:
    showtime_dict_musicbox = pickle.load(file)

with open('data/showtimes/musicbox_film_details_dict.pkl', 'rb') as file:
    prod_info_dict_musicbox = pickle.load(file)


# Examine dictionary overlap
# print('Siskel films not in Music Box:')
# for film in showtime_dict_siskel:
#       if film not in showtime_dict_musicbox:
#             print(film)

# print('\nMusic Box films not in Siskel:')
# for film in showtime_dict_musicbox:
#       if film not in showtime_dict_siskel:
#             print(film)


siskel_list = list(showtime_dict_siskel.keys())
musicbox_list = list(showtime_dict_musicbox.keys())
# print(musicbox_list)

# for film in siskel_list:
#       if film in musicbox_list:
#             print(film)

# for film in musicbox_list:
#       if film in siskel_list:
#             print(film)


master_dict = {}

siskel_missing_year = []
for film in showtime_dict_siskel:
    if 'Release Year' in prod_info_dict_siskel[film]:
            master_dict[film] = {
                'Title': film.upper(),
                'Release Year': prod_info_dict_siskel[film]['Release Year'],
            }

            if 'Director' in prod_info_dict_siskel[film]:
                master_dict[film]['Director'] = prod_info_dict_siskel[film]['Director']
    else:
            siskel_missing_year.append(film)

musicbox_missing_year = []
for film in showtime_dict_musicbox:
    if 'Year' in prod_info_dict_musicbox[film]:
            master_dict[film] = {
                'Title': film.upper(),
                'Release Year': prod_info_dict_musicbox[film]['Year'],
            }

            if 'Director' in prod_info_dict_musicbox[film]:
                master_dict[film]['Director'] = prod_info_dict_musicbox[film]['Director']

master_titles_yrs_df = pd.DataFrame(master_dict).T.reset_index(drop=True)
master_titles_yrs_df.to_csv('data/showtimes/showtime_master_titles_yrs.csv', index=False)
print(master_titles_yrs_df)

master_detail_scrape_df = mc_film_detail_scrape(master_titles_yrs_df, 
                    driver,
                #     test_n_films=130,
                    output_filename='showtime_mc_detail_scrape',
                    )

print(master_detail_scrape_df)
    
# print('Siskel films missing year:\n', siskel_missing_year)
# print('Music Box films missing year:\n', musicbox_missing_year)