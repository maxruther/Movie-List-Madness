from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup

import pandas as pd

import time
from datetime import datetime, timezone
import pytz

import pickle

from typing import Dict, Tuple

if __name__ == '__main__':
    from utils import parse_show_name, print_runtime_of_scrape, create_chromedriver, save_output_df_to_dirs, save_scrape_and_add_to_existing, save_driver_html_to_file
else:
    try:
        from its_showtimes.scrapers.utils import parse_show_name, print_runtime_of_scrape, create_chromedriver, save_output_df_to_dirs, save_scrape_and_add_to_existing, save_driver_html_to_file
    except:
        try:
            from scrapers.utils import parse_show_name, print_runtime_of_scrape, create_chromedriver, save_output_df_to_dirs, save_scrape_and_add_to_existing, save_driver_html_to_file
        except:
            raise Exception("\n'siskel_scrape' ERROR: Failed to import methods from my utils.py\n")

import re
import os


def siskel_scrape(
        test_n_films: int = 0,
        ) -> Tuple[
            Dict[str, datetime],
            pd.DataFrame,
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
    driver = create_chromedriver()
    driver.implicitly_wait(3)

    # This is the link to the Siskel's film calendar. It show's the
    # current month's calendar by default.
    film_calendar_link = 'https://www.siskelfilmcenter.org/playing-this-month'
    
    # From that link, create a list that will also include the next
    # month's calendar's link, if it exists.
    calendar_links = [film_calendar_link]

    # Navigate to the film calendar page.
    driver.get(film_calendar_link)

    # Save this page's source code to file, for debugging purposes.
    html_data_subdir = 'siskel'
    save_driver_html_to_file(driver, html_data_subdir)

    # # Get the next month's calendar's link, if it exists.
    # Locate the "Next Month" button.
    next_month_button_element = None
    try:
        next_month_button_element = driver.find_element(By.CSS_SELECTOR, 
                                                    'div.next-month')
    except:
        print("WARNING: Could not identify next month's calendar.")
        time.sleep(3)
    
    # If the button exists, click it to get the next month's calendar.
    if next_month_button_element:
        next_month_button_element.click()
        calendar_links.append(driver.current_url)

        # Save this page's source code to file, for debugging purposes.
        save_driver_html_to_file(driver, html_data_subdir)

        # Navigate back to the current month's calendar.
        driver.get(film_calendar_link)


    # Initialize a dictionary and list that will ultimately form the
    # showtime and film info datasets, the concerns of this scrape.
    show_info_dict = {}
    film_showtimes_list = []


    # To time the scrape, note the current time as its start.
    scrape_start = time.time()

    # Mark the datetime of this running of the scrape.
    scrape_datetime_str = datetime.now(timezone.utc).isoformat()

    # # Iterate through the month calendars. 
    # (If testing, only process the first month's calendar.)
    if test_n_films:
        calendar_links = [film_calendar_link]
    for cal_link in calendar_links:

        # Create a BeautifulSoup object from this month's calendar page.
        driver.get(cal_link)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Form an iterable of all its shows
        shows = soup.select('li.calendar-view-day__row')

        # Iterate through each of the calendar's shows to scrape the
        # films' info and showtimes.
        # (If testing, only scrape the first n shows.)
        if test_n_films:
            if test_n_films <= len(shows):
                shows = shows[:test_n_films]
        for show in shows:

            # Get the show title and film title from the show element.
            # (These tend to differ when the show is part of a series,
            # where the show title includes the series' name as a 
            # prefix.)
            show_title, film_title = None, None
            show_title_elem = show.select_one('div.views-field.views-field-title')
            if show_title_elem:
                show_title = show_title_elem.text.strip()
                # print(show_title)
                film_title, _ = parse_show_name(show_title)
            
            # Get the show's date and time.
            showtime_datetime = None
            show_time_elem = show.select_one('time')
            if show_time_elem:
                showtime_str = show_time_elem.get('datetime')
                # showtime_datetime = datetime.fromisoformat(showtime_str).astimezone()

                showtime_datetime = datetime.strptime(showtime_str, "%Y-%m-%dT%H:%M:%SZ")
                showtime_datetime = showtime_datetime.replace(tzinfo=pytz.UTC)
                showtime_datetime = showtime_datetime.isoformat()
                print(showtime_datetime)

            # Get the link to the show's dedicated page.
            # (This is where the film's info is found.)
            link = None
            show_link_elem = show.select_one('a')
            if show_link_elem:
                link = 'https://www.siskelfilmcenter.org/' + show_link_elem.get('href')
                # print(link)

            # If the film's title has yet to be documented in the show
            # info dictionary, scrape its info from the film's dedicated
            # page.
            # (Initialize to none the variables 'year' and 'directors',
            # which will form a primary key for many tables downstream.)
            year, directors = None, None
            if link and film_title not in show_info_dict:
                
                # Skip processing the 'Mystery Movie Monday' pages.
                if 'Mystery Movie Monday' in show_title:
                    continue

                # Navigate to the movie's dedicated page.
                driver.get(link)

                # Have the driver wait until the page's key content is
                # loaded.
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.content')))
                except TimeoutException:
                    print ("Loading took too much time - 'div.content' not found.")

                # Create a BeautifulSoup object from the page's source 
                # code.
                show_page_soup = BeautifulSoup(driver.page_source, 'html.parser')

                # Get the show's series name, if it exists.
                series = None
                film_header_elem = show_page_soup.select_one('div.content')
                if film_header_elem:
                    series_elem = film_header_elem.select_one('div.film-header-series')
                    if series_elem:
                        series = series_elem.text.strip()
                
                # Get other tags of the show, if they exist.
                tags = None
                tags_elem = film_header_elem.select_one('div.film-header-headline')
                if tags_elem:
                    tags = tags_elem.text.strip()
                
                # Get the screened film's year, directors, country, and
                # runtime. These share a string, separated by commas.
                year, directors, country, runtime = None, None, None, None
                country_yr_elem = film_header_elem.select_one('div.film-header-country-year')
                if country_yr_elem:
                    country_yr_text = country_yr_elem.text.strip()

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
                        # (Need to take only one year in order for the 
                        # field to be valid as an "int" in the database,
                        #  down the line.)
                        year = re.search(yr_pattern, year).group(1)
                    print(show_title, year)

                    if not re.search(runtime_pattern, runtime):
                        print('INVALID RUNTIME:', show_title, runtime)
                    else:
                        runtime = re.search(runtime_pattern, runtime).group(1)
                
                # Get the 'meta' info, if it exists, which tends to
                # state the film's format (e.g. 36mm) and its spoken
                # language.)
                meta = None
                meta_elem = film_header_elem.select_one('div.film-header-meta')
                if meta_elem:
                    meta = meta_elem.text.strip()

                # Get the show's description.
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
                
                # Create the record of this show's info, by forming that
                # info into a dictionary (within the greater 'show info'
                # dictionary.)
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
                    'Theater': 'Siskel',
                    'Scrape_Datetime': scrape_datetime_str,
                    
                    }
                
                
                # # Print the new film's info, just scraped.
                # print(film_title)
                # for field_value in show_info_dict[film_title].values():
                #     print(field_value)
                # print()

            # If the film has already been documented in the show info
            # dictionary, get its year and directors from there.
            if film_title in show_info_dict:
                year = show_info_dict[film_title].get('Year', None)
                directors = show_info_dict[film_title].get('Director', None)

            # Create a record of this show's showtime, by forming that
            # info into a dictionary and adding that to the list of all
            # showtimes.
            showtime_entry = {
                'Title': film_title,
                'Year': year,
                'Director': directors,
                'Showtime': showtime_datetime,
                'Theater': 'Siskel',
                'Scrape_Datetime': scrape_datetime_str,
                
                }
            
            if showtime_entry not in film_showtimes_list:
                film_showtimes_list.append(showtime_entry)


    # # With the scrape now concluded, this process turns to file-saving.


    # Create dataframes of the scraped showtimes and show info.
    new_showtimes_df = pd.DataFrame(film_showtimes_list)

    new_info_df = pd.DataFrame.from_dict(show_info_dict, orient='index').reset_index()
    new_info_df.rename(columns={'index': 'Title'}, inplace=True)


    # Set the names of the output files and their parent dir (as the 
    # subdir of 'data/pkl' and 'data/csv'.)
    showtimes_filename = 'siskel_showtimes'
    info_filename = 'siskel_show_info'
    output_subdir = 'siskel'

    # Save this scrape to file, and also add its data to any existing
    # data-scrape files.
    save_scrape_and_add_to_existing(
        new_showtimes_df, showtimes_filename, output_subdir, test_n_films
        )
    save_scrape_and_add_to_existing(
        new_info_df, info_filename, output_subdir, test_n_films
        )

    
    # Note and print scrape's runtime.
    print_runtime_of_scrape(scrape_start)

    # Quit and close the driver, to conclude.
    driver.quit()

    return new_showtimes_df, new_info_df


if __name__ == '__main__':

    # Run the Siskel scrape
    # showtimes_df, info_df = siskel_scrape()
    showtimes_df, info_df = siskel_scrape(test_n_films=20000)
