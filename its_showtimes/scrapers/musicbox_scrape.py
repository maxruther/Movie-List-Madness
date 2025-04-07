from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

import time
from datetime import datetime

import pickle
import re

import pandas as pd

from typing import Dict, Tuple

import os


if __name__ != '__main__':
    from scrapers.utils import tech_summary_list_to_dict
else:
    from utils import tech_summary_list_to_dict


def musicbox_scrape(
        testing: bool = False,
        ) -> Tuple[
            Dict[str, datetime],
            pd.DataFrame
            ]:
    
    # Set up the Selenium ChromeDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options)

    # Navigate the driver to the Music Box calendar page.
    mb_calendar_link = 'https://musicboxtheatre.com/films-and-events'
    driver.get(mb_calendar_link)

    # Check for second page of calendar, if it exists.
    next_month_button_xpath = '/html/body/div[1]/main/div/div[2]/div/div/div/div[1]/div[2]/a[2]'
    next_month_button_element = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.XPATH, next_month_button_xpath))
    )

    calendar_page_links = [mb_calendar_link]

    if next_month_button_element:
        next_month_cal_link = next_month_button_element.get_attribute('href')
        calendar_page_links.append(next_month_cal_link)


    # # For testing purposes, load old calendar text from a pickle file.
    # with open('data/showtimes/test_mb_calendar_text.pkl', 'rb') as file:
    #     calendar_text = pickle.load(file)

    # films_showtimes = {}
    showtimes_list = []
    film_details = {}

    # Time the imminent scraping by first
    # noting its start (for the dev's reference.)
    scrape_start = time.time()

    # Iterate through each calendar page, scraping the showtimes and film details.
    if testing:
        # Test on just this month's calendar.
        calendar_page_links = [mb_calendar_link]
    for cal_link in calendar_page_links:
        driver.get(cal_link)

        calendar_elem_xpath = '/html/body/div[1]/main/div/div[2]/div/div/div/div[2]'
        calendar_text = driver.find_element(By.XPATH, calendar_elem_xpath).get_attribute('innerHTML')
        soup = BeautifulSoup(calendar_text, 'html.parser')

        calendar_days = soup.select('div.calendar-cell')

        
        if testing:
            # Test on just the last handful of days in the calendar.
            calendar_days = calendar_days[-10:]
        for day in calendar_days:
            if 'calendar-head' in day.get('class'):
                # print('EMPTY CALENDAR CELL - HEADER')
                pass
            elif 'empty' in day.get('class'):
                # print('EMPTY CALENDAR CELL - PAST DATE')
                pass
            else:
                calendar_date_elem = day.select_one('div.calendar-date')
                date_text_all = calendar_date_elem.text.strip().split(', ')
                date_str = ' '.join(date_text_all[-2:])

            
            shows = day.select('div.programming-content')
            for show in shows:

                show_title = show.select_one('a').text.strip().upper()

                # Remove parenthesized release year from the show/film title string, if present.
                pattern = r'(.*)\ \((\d{4})\)$'
                if re.search(pattern, show_title):
                    show_title = re.search(pattern, show_title).groups()[0]

                show_tags = show.select_one('div.tags').text.strip()
                if show_tags:
                    """
                    # Series Handling
                    if show_tags == 'Film Series':
                        series_relative_link = show.select_one('a').get('href')
                        print(series_relative_link)
                        series_link = 'https://musicboxtheatre.com' + series_relative_link
                        driver.get(series_link)
                    """

                showtimes_elem = show.select_one('div.programming-showtimes')

                if showtimes_elem:

                    if show_title not in film_details:
                        show_rel_link = show.select_one('a').get('href')
                        show_link = 'https://musicboxtheatre.com' + show_rel_link
                        # print(show_link)
                        driver.get(show_link)
                        main_section_xpath = '/html/body/div[1]/main'
                        main_section_text = driver.find_element(By.XPATH, value=main_section_xpath).get_attribute('innerHTML')
                        main_section_soup = BeautifulSoup(main_section_text, 'html.parser')

                        tech_summary_elem = main_section_soup.select_one('p.tech-summary')
                        if tech_summary_elem:
                            tech_summ_deets = tech_summary_elem.select('span')
                            tech_deet_list = [deet.text.strip() for deet in tech_summ_deets]
                        film_details[show_title] = tech_summary_list_to_dict(tech_deet_list)
                        if 'Year' not in film_details[show_title]:
                            film_details[show_title]['Year'] = None

                        credit_elems = main_section_soup.select('div.credits')
                        print(f'\n\n{show_title} - Credits:')

                        film_details[show_title]['Director'] = None
                        for credit_elem in credit_elems:
                            credit_type = credit_elem.find('label').text.strip()
                            if credit_type == 'DIRECTED BY':
                                director_elems = credit_elem.select('span')
                                director = ', '.join([director_elem.text.strip(' ,') for director_elem in director_elems])
                                print(f'{credit_type}: {director}')
                                film_details[show_title]['Director'] = director
                            elif credit_type == 'WRITTEN BY':
                                writer_elems = credit_elem.select('span')
                                writer = ', '.join([writer_elem.text.strip(' ,') for writer_elem in writer_elems])
                                print(f'{credit_type}: {writer}')
                                film_details[show_title]['Writer'] = writer
                            elif credit_type == 'STARRING':
                                cast_elems = credit_elem.select('span')
                                cast = ', '.join([cast_elem.text.strip(' ,') for cast_elem in cast_elems])
                                print(f'{credit_type}: {cast}')
                                film_details[show_title]['Cast'] = cast

                    showtimes = showtimes_elem.select('a.use-ajax')
                    # print(f'Showtimes:')
                    for showtime in showtimes:
                        showtime_str = showtime.text.replace('"', '')

                        date_and_showtime = date_str + ' ' + showtime_str
                        showtime_datetime = datetime.strptime(date_and_showtime, 
                                                            '%b %d %Y %I:%M%p')
                        # print(showtime_datetime)

                        # if show_title not in films_showtimes:
                        #     films_showtimes[show_title] = [showtime_datetime]
                        # else:
                        #     if showtime_datetime not in films_showtimes[show_title]:
                        #         films_showtimes[show_title].append(showtime_datetime)
                        
                        showtime_record_dict = {
                            'Title': show_title,
                            'Year': film_details[show_title]['Year'],
                            'Director': film_details[show_title]['Director'],
                            'Showtime': showtime_datetime,
                        }
                        showtimes_list.append(showtime_record_dict)

    
    # # Printing the various outputs of the scrape.
    # for pair in film_details.items():
    #     print(pair)
    # print()
    # print(films_showtimes, '\n\n')
    # print(film_details)


    # # Saving the scraped data to files.

    # Set the filepaths of the directories that
    # will house the scraped data.
    output_dir_pkl = 'data/pkl/musicbox'
    output_dir_csv = 'data/csv/musicbox'

    if testing:
        output_dir_pkl += '/test'
        output_dir_csv += '/test'

    os.makedirs(output_dir_pkl, exist_ok=True)
    os.makedirs(output_dir_csv, exist_ok=True)

    # Create and save a dataframe of the scraped show info.
    info_df = pd.DataFrame.from_dict(film_details, orient='index').reset_index()
    info_df.rename(columns={'index': 'Title'}, inplace=True)

    info_filename = 'musicbox_show_info'
    if testing:
        info_filename = 'test_' + info_filename
    
    info_df.to_csv(f'{output_dir_csv}/{info_filename}.csv', index=False)
    info_df.to_pickle(f'{output_dir_pkl}/{info_filename}.pkl')

    # # Save the showtimes and show info dictionaries to pkl files.
    # with open(f'data/pkl/musicbox/musicbox_showtimes_dict.pkl', 'wb') as file:
    #     pickle.dump(films_showtimes, file)
    # with open(f'data/pkl/musicbox/musicbox_show_info_dict.pkl', 'wb') as file:
    #     pickle.dump(film_details, file)

    
    # Create and save a dataframe of the scraped showtimes.
    showtimes_df = pd.DataFrame(showtimes_list)
    showtimes_df['Showtime_Date'] = showtimes_df['Showtime'].dt.date
    showtimes_df['Showtime_Time'] = showtimes_df['Showtime'].dt.time

    showtimes_filename = 'musicbox_showtimes'
    if testing:
        showtimes_filename = 'test_' + showtimes_filename
    
    showtimes_df.to_csv(f'{output_dir_csv}/{showtimes_filename}.csv', index=False)
    showtimes_df.to_pickle(f'{output_dir_pkl}/{showtimes_filename}.pkl')


    # Note the scrape's runtime.
    scrape_runtime = time.time() - scrape_start
    scrape_runtime = round(scrape_runtime)
    runtime_min = scrape_runtime // 60
    runtime_sec = scrape_runtime % 60
    scrape_runtime_str = f'{runtime_min} m {runtime_sec} s'
    print(f'\nRuntime of this scrape: {scrape_runtime_str}')

    # Quit and close the driver, to conclude.
    driver.quit()

    return showtimes_df, info_df


if __name__ == '__main__':

    # Run the Music Box scrape
    # showtime_dict, show_info_df = musicbox_scrape(testing=True)
    showtime_dict, show_info_df = musicbox_scrape()

    # Print previews of the scraped output:
    
    # Showtimes
    for movie, showtime_list in list(showtime_dict.items())[:5]:
        print(movie)
        for showtime in showtime_list:
            print(f'\t{showtime}')
        print()
    
    # A separator
    print('\n' + '-'*80 + '\n')

    # Show info
    print(show_info_df.head(), '\n')
