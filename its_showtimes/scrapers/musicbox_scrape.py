from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

import time
from datetime import datetime
import re

import pandas as pd

from typing import Dict, Tuple


if __name__ == '__main__':
    from utils import tech_summary_list_to_dict, print_runtime_of_scrape, create_chromedriver, save_output_df_to_dirs
else:
    try:
        from its_showtimes.scrapers.utils import tech_summary_list_to_dict, print_runtime_of_scrape, create_chromedriver, save_output_df_to_dirs
    except:
        try:
            from scrapers.utils import tech_summary_list_to_dict, print_runtime_of_scrape, create_chromedriver, save_output_df_to_dirs
        except:
            raise Exception("\n'musicbox_scrape' ERROR: Failed to import method 'tech_summary_list_to_dict'\n")


def musicbox_scrape(
        test_n_days: bool = False,
        ) -> Tuple[
            Dict[str, datetime],
            pd.DataFrame
            ]:
    
    # Set up the Selenium ChromeDriver
    driver = create_chromedriver()

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
    if test_n_days:
        # Test on just this month's calendar.
        calendar_page_links = [mb_calendar_link]
    for cal_link in calendar_page_links:
        driver.get(cal_link)

        calendar_elem_xpath = '/html/body/div[1]/main/div/div[2]/div/div/div/div[2]'
        calendar_text = driver.find_element(By.XPATH, calendar_elem_xpath).get_attribute('innerHTML')
        soup = BeautifulSoup(calendar_text, 'html.parser')

        calendar_days_ahead = soup.select('div.calendar-cell:not(.past):not(.empty):not(.calendar-head)')
        for day in list(calendar_days_ahead)[:test_n_days]:
            print(day.text.strip(), end='\n' + '-'*80 + '\n\n')

        
        if test_n_days:
            if test_n_days < len(calendar_days_ahead):
                calendar_days_ahead = list(calendar_days_ahead)[:test_n_days]
            else:
                raise ValueError(f"ERROR: In this current month, there aren't {test_n_days} days ahead for testing.")
            
        for day in calendar_days_ahead:
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
                        # print(f'\n\n{show_title} - Credits:')

                        film_details[show_title]['Director'] = None
                        for credit_elem in credit_elems:
                            credit_type = credit_elem.find('label').text.strip()
                            if credit_type == 'DIRECTED BY':
                                director_elems = credit_elem.select('span')
                                director = ', '.join([director_elem.text.strip(' ,') for director_elem in director_elems])
                                # print(f'{credit_type}: {director}')
                                film_details[show_title]['Director'] = director
                            elif credit_type == 'WRITTEN BY':
                                writer_elems = credit_elem.select('span')
                                writer = ', '.join([writer_elem.text.strip(' ,') for writer_elem in writer_elems])
                                # print(f'{credit_type}: {writer}')
                                film_details[show_title]['Writer'] = writer
                            elif credit_type == 'STARRING':
                                cast_elems = credit_elem.select('span')
                                cast = ', '.join([cast_elem.text.strip(' ,') for cast_elem in cast_elems])
                                # print(f'{credit_type}: {cast}')
                                film_details[show_title]['Cast'] = cast

                    showtimes = showtimes_elem.select('a.use-ajax')
                    # print(f'Showtimes:')
                    for showtime in showtimes:
                        showtime_str = showtime.text.replace('"', '')

                        date_and_showtime = date_str + ' ' + showtime_str
                        showtime_datetime = datetime.strptime(date_and_showtime, 
                                                            '%b %d %Y %I:%M%p')
                        # print(showtime_datetime)
                        
                        showtime_record_dict = {
                            'Title': show_title,
                            'Year': film_details[show_title]['Year'],
                            'Director': film_details[show_title]['Director'],
                            'Showtime': showtime_datetime,
                            'Showtime_Date': showtime_datetime.date(),
                            'Showtime_Time': showtime_datetime.time(),
                        }
                        showtimes_list.append(showtime_record_dict)


    # # Saving the scraped data to files.

    # Create dataframes of the scraped showtimes and show info.
    showtimes_df = pd.DataFrame(showtimes_list)

    info_df = pd.DataFrame.from_dict(film_details, orient='index').reset_index()
    info_df.rename(columns={'index': 'Title'}, inplace=True)

    # Set the names of the output files and their parent dir (as the 
    # subdir of 'data/pkl' and 'data/csv'.)
    showtimes_filename = 'musicbox_showtimes'
    info_filename = 'musicbox_show_info'
    output_subdir = 'musicbox'

    # Accordingly, save the dataframes as pkl and csv files.
    save_output_df_to_dirs(showtimes_df, test_n_days, showtimes_filename, output_subdir)
    save_output_df_to_dirs(info_df, test_n_days, info_filename, output_subdir)


    # Note the scrape's runtime.
    print_runtime_of_scrape(scrape_start)

    # Quit and close the driver, to conclude.
    driver.quit()

    return showtimes_df, info_df


if __name__ == '__main__':

    # Run the Music Box scrape
    # showtimes_df, info_df = musicbox_scrape(test_n_days=2)
    showtimes_df, info_df = musicbox_scrape()
