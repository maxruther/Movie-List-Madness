from selenium import webdriver
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

import time
from datetime import datetime

import pickle
import re

import pandas as pd


# Load the dictionary of scraped Siskel showtimes.
with open('data/showtimes/siskel_films_showtimes_dict.pkl', 'rb') as file:
    showtime_dict_siskel = pickle.load(file)


# Set up the Selenium Chromium driver
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
driver = webdriver.Chrome(options)


# Get HTML of the "Coming Soon" page.
driver.get('https://www.siskelfilmcenter.org/coming-soon')
coming_soon_html = driver.page_source
with open('data/showtimes/coming_soon_html_2025-03-08.pkl', 'wb') as file:
    pickle.dump(coming_soon_html, file)

# Get HTML of the "Now Playing" page.
driver.get('https://www.siskelfilmcenter.org/now-playing')
now_playing_html = driver.page_source
with open('data/showtimes/now_playing_html_2025-03-09.pkl', 'wb') as file:
    pickle.dump(now_playing_html, file)

# # For testing, load from file saved pages for "Coming Soon" and "Now Playing."
# with open('data/showtimes/now_playing_html_2025-03-09.pkl', 'rb') as file:
#     now_playing_html = pickle.load(file)

# with open('data/showtimes/coming_soon_html_2025-03-08.pkl', 'rb') as file:
#     coming_soon_html = pickle.load(file)


screening_pages = [now_playing_html, coming_soon_html]
for page_html in screening_pages:


    page_soup = BeautifulSoup(page_html, 'html.parser')
    movie_tiles = page_soup.find_all('div', class_='grid-all-overlay-inner')

    show_info_dict = {}
    for movie_tile in movie_tiles:
        show_name, dir_and_yr = movie_tile.text.strip().split('\n')

        dir_and_yr_pattern = r"(.*?) (\d+(?:, \d+)?)"
        dir_and_yr_match =  re.match(dir_and_yr_pattern, dir_and_yr)
        dir, yr = None, None
        if dir_and_yr_match:
            dir, yr = re.match(dir_and_yr_pattern, dir_and_yr).groups()
        
        show_info_dict[show_name] = {
            'Director': dir,
            'Year': yr,
        }

        link = movie_tile.find('a')['href']
        if link:
            show_info_dict[show_name]['Link'] = 'https://www.siskelfilmcenter.org' + link

        # print(show_name,
        #       coming_soon_movies[show_name]['Director'],
        #       coming_soon_movies[show_name]['Year'],
        #       coming_soon_movies[show_name]['Link'],
        #       sep='\n', end='\n\n')


        if link:
            
            # Skip the 'Mystery Movie Monday' pages
            if 'Mystery Movie Monday' in show_name:
                continue

            # Navigate to the movie's dedicated page and create a soup 
            # object therefrom.
            driver.get(show_info_dict[show_name]['Link'])
        
            film_details_html = driver.page_source
            film_details_soup = BeautifulSoup(film_details_html, 'html.parser')

            # print(show_name)
            film_header_elem = film_details_soup.select_one('div.content')

            series = None
            series_elem = film_header_elem.select_one('div.film-header-series')
            if series_elem:
                series = series_elem.text.strip()
                if series:
                    show_info_dict[show_name]['Series'] = series
            
            tags = None
            tags_elem = film_header_elem.select_one('div.film-header-headline')
            if tags_elem:
                tags = tags_elem.text.strip()
                if tags:
                    show_info_dict[show_name]['Tags'] = tags
            
            year, directors, country, runtime = None, None, None, None
            country_yr_elem = film_header_elem.select_one('div.film-header-country-year')
            if country_yr_elem:
                country_yr_text = country_yr_elem.text.strip()
                # print(country_yr_text)

                if country_yr_text == ', Unknown, Unknown,':
                    continue

                entries = country_yr_text.split(', ')

                runtime = entries[-1]
                country = entries[-2]

                year_list = []
                dir_list = []
                for entry in entries[:-2]:
                    if re.search(r'^\d{4}$', entry):
                        year_list.append(entry)
                    else:
                        dir_list.append(entry)
                year = ', '.join(year_list)
                directors = ', '.join(dir_list)

                yr_pattern = r'^(\d+(?:, \d+)?)$'
                runtime_pattern = r'^(\d*) mins?$'

                if not re.search(yr_pattern, year):
                    print('INVALID YEAR:', show_name, year)

                if not re.search(runtime_pattern, runtime):
                    print('INVALID RUNTIME:', show_name, runtime)
                else:
                    runtime = re.search(runtime_pattern, runtime).group(1)
                    
                
                if year:
                    show_info_dict[show_name]['Year'] = year
                if runtime:
                    show_info_dict[show_name]['Runtime'] = runtime
                if directors:
                    show_info_dict[show_name]['Director'] = directors
                if country:
                    show_info_dict[show_name]['Country'] = country

                # print(year, runtime, directors,country,  sep='\n', end='\n\n')

            
            meta = None
            meta_elem = film_header_elem.select_one('div.film-header-meta')
            if meta_elem:
                meta = meta_elem.text.strip()
                show_info_dict[show_name]['Meta'] = meta

with open("data/showtimes/siskel_show_info_scr_dict.pkl", 'wb') as file:
    pickle.dump(show_info_dict, file)

siskel_show_info_df = pd.DataFrame(show_info_dict).T
siskel_show_info_df = siskel_show_info_df.rename_axis('Show Name')

siskel_show_info_df.to_csv('data/showtimes/siskel_show_info_scrape.csv')
siskel_show_info_df.to_pickle('data/showtimes/siskel_show_info_scrape.pkl')


driver.quit()