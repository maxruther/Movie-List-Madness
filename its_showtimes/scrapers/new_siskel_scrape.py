from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup

import pandas as pd

import time
from datetime import datetime

import pickle

from typing import Dict, Tuple

from utils import parse_show_name

import re


# if __name__ == '__main__':
#     from utils import parse_show_name
# else:
#     from scrapers.utils import parse_show_name


def new_siskel_scrape(
        test_n_films: int = 0,
) -> Tuple[
    Dict[str, datetime],
    pd.DataFrame
    #   Dict[str, Dict[str, str]]
    ]:
    """Scrape the Siskel Film Center's show calendar to get showtimes
    and some info on those films.
    
    Given a Selenium Chrome webdriver, returns:
    
    1. A showtime dictionary: each key is a film and each value is a
           list of showtimes, as listed datetime objects.

    2. A production-info dictionary: each key is a film and each
           value is a dictionary containing a few production details,
           like release year, runtime, and director.
    """

    # Set up the Selenium Chromium driver
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options)

    driver.implicitly_wait(3)

    # # Pull up the Siskel's show calendar, which involves navigating to
    # # the calendar page and then clicking the button/link titled
    # # "Calendar".
    # siskel_link = 'https://www.siskelfilmcenter.org/calendar'
    # driver.get(siskel_link)
    # calendar_link_xpath = '/html/body/div[1]/div[4]/div/section/div[2]/article/div/div/p/a'
    # true_calendar_element = driver.find_element(By.XPATH, calendar_link_xpath)
    # true_calendar_link = true_calendar_element.get_attribute('href')

    true_calendar_link = 'https://www.siskelfilmcenter.org/playing-this-month'
    driver.get(true_calendar_link)

    next_month_button_element = None
    try:
        next_month_button_element = driver.find_element(By.CSS_SELECTOR, 
                                                    'div.next-month')
    except:
        print("WARNING: Could not identify next month's calendar.")
        time.sleep(3)
    
    calendar_links = [true_calendar_link]

    if next_month_button_element:
        next_month_button_element.click()
        calendar_links.append(driver.current_url)

        driver.get(true_calendar_link)


    # Initialize lists and dicts that will ultimately form the output
    # datasets.

    show_info_dict = {}

    film_showtimes_2_list = []


    # To time the scrape, note the current time as its start.
    scrape_start = time.time()


    # Iterate through the month calendars. If testing, only process the
    # first month's calendar.
    if test_n_films:
        calendar_links = [true_calendar_link]
    for cal_link in calendar_links:

        # Create a BeautifulSoup object from this month's calendar page.
        driver.get(cal_link)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Form an iterable of all its shows
        shows = soup.select('li.calendar-view-day__row')


        # Iterate through each of the calendar's shows to scrape the
        # films' info and showtimes.

        # If testing, only check first n shows.
        if test_n_films:
            if test_n_films <= len(shows):
                shows = shows[:test_n_films]
        for show in shows:

            show_title, film_title = None, None
            show_title_elem = show.select_one('div.views-field.views-field-title')
            if show_title_elem:
                show_title = show_title_elem.text.strip()
                # print(show_title)
                film_title, _ = parse_show_name(show_title)
            
            showtime_datetime = None
            show_time_elem = show.select_one('time')
            if show_time_elem:
                show_time_str = show_time_elem.get('datetime')
                showtime_datetime = datetime.fromisoformat(show_time_str)
                # print(showtime_datetime)

            link = None
            show_link_elem = show.select_one('a')
            if show_link_elem:
                link = 'https://www.siskelfilmcenter.org/' + show_link_elem.get('href')
                # print(link)

            
            year, directors = None, None
            if link and film_title not in show_info_dict:
                
                # Skip the 'Mystery Movie Monday' pages
                if 'Mystery Movie Monday' in show_title:
                    continue

                # Navigate to the movie's dedicated page and create a soup 
                # object therefrom.
                # driver.get(show_info_dict[show_title]['Link'])
                driver.get(link)

                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.content')))
                except TimeoutException:
                    print ("Loading took too much time - 'div.content' not found.")

                show_page_soup = BeautifulSoup(driver.page_source, 'html.parser')

                series = None
                film_header_elem = show_page_soup.select_one('div.content')
                if film_header_elem:
                    series_elem = film_header_elem.select_one('div.film-header-series')
                    if series_elem:
                        series = series_elem.text.strip()
                        # if series:
                        #     show_info_dict[show_title]['Series'] = series
                
                tags = None
                tags_elem = film_header_elem.select_one('div.film-header-headline')
                if tags_elem:
                    tags = tags_elem.text.strip()
                    # if tags:
                    #     show_info_dict[show_title]['Tags'] = tags
                
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

                    yr_pattern = r'^(\d{4})(?:, \d{4})?$'
                    runtime_pattern = r'^(\d*) mins?$'

                    if not re.search(yr_pattern, year):
                        print('INVALID YEAR:', show_title, year)
                    else:
                        # Take the first (earliest?) year listed. 
                        # (Need to take only one year in order for the field to be valid as an "int" in the database, down the line.)
                        year = re.search(yr_pattern, year).group(1)
                    print(show_title, year)

                    if not re.search(runtime_pattern, runtime):
                        print('INVALID RUNTIME:', show_title, runtime)
                    else:
                        runtime = re.search(runtime_pattern, runtime).group(1)
                
                meta = None
                meta_elem = film_header_elem.select_one('div.film-header-meta')
                if meta_elem:
                    meta = meta_elem.text.strip()

                
                description = None
                main_content_elem = show_page_soup.select_one('div.main-container.container')
                if main_content_elem:
                    summary_text_elem = main_content_elem.select_one('div.field--type-text-with-summary')
                    if summary_text_elem:
                        desc_elem = summary_text_elem.select_one('p')
                        if desc_elem:
                            description = desc_elem.text.strip()
                            if '|' in description:
                                description = description.split('|')[1].strip()
                
                show_info_dict[film_title] = {
                    # 'Title': film_title,
                    'Year': year,
                    'Director': directors,
                    'Runtime': runtime,
                    'Series': series,
                    'Tags': tags,
                    'Country': country,
                    'Meta': meta,
                    'Link': link,
                    'Show': show_title,
                    'Description': description,
                    }
                
                
                # # Print the new film's info, just scraped.
                # print(film_title)
                # for field_value in show_info_dict[film_title].values():
                #     print(field_value)
                # print()


            if film_title in show_info_dict:
                year = show_info_dict[film_title].get('Year', None)
                directors = show_info_dict[film_title].get('Director', None)

            showtime_entry = {
                'Title': film_title,
                'Year': year,
                'Director': directors,
                'Showtime': showtime_datetime,
                'Showtime_Date': showtime_datetime.date(),
                'Showtime_Time': showtime_datetime.time(),
            }
            film_showtimes_2_list.append(showtime_entry)

    # Set desired filepaths for the directories of the outputted 
    # dataframes.
    siskel_scrape_pkl_dir = 'data/pkl/siskel/scrape_v2'
    siskel_scrape_csv_dir = 'data/csv/siskel/scrape_v2'

    # Create and save a dataframe of the show info scraped.

    # info_df = pd.DataFrame(show_info_dict).T
    # info_df = info_df.rename_axis('Title')

    info_df = pd.DataFrame.from_dict(show_info_dict, orient='index')
    info_df.index.name = 'Title'
    info_df = info_df.reset_index()
    
    info_filename = 'siskel_show_info'
    info_df.to_pickle(f'{siskel_scrape_pkl_dir}/{info_filename}.pkl')
    info_df.to_csv(f'{siskel_scrape_csv_dir}/{info_filename}.csv')

    # Create and save a dataframe of the showtimes scraped.
    showtimes_df = pd.DataFrame(film_showtimes_2_list)

    showtimes_filename = 'siskel_showtimes'
    showtimes_df.to_pickle(f'{siskel_scrape_pkl_dir}/{showtimes_filename}.pkl')
    showtimes_df.to_csv(f'{siskel_scrape_csv_dir}/{showtimes_filename}.csv', index=False)


    # Note and print the runtime of the scrape.
    scrape_runtime = time.time() - scrape_start
    scrape_runtime = round(scrape_runtime)
    runtime_min = scrape_runtime // 60
    runtime_sec = scrape_runtime % 60
    scrape_runtime_str = f'{runtime_min} m {runtime_sec} s'
    print(f'\nRuntime of this Siskel scrape: {scrape_runtime_str}')

    # Quit and close the driver, to conclude.
    driver.quit()

    # return films_showtimes, film_details_df

if __name__ == '__main__':

    # Run the Siskel scrape
    new_siskel_scrape()
    # showtime_dict, inferior_info_df = new_siskel_showtime_scrape()

    # # # Print previews of the scraped output:
    
    # # Showtimes
    # for movie, showtime_list in list(showtime_dict.items())[:5]:
    #     print(movie)
    #     for showtime in showtime_list:
    #         print(f'\t{showtime}')
    #     print()
    
    # # A separator
    # print('\n' + '-'*80 + '\n')

    # # Show info
    # print(inferior_info_df.head(), '\n')

