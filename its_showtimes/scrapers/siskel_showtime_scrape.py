from selenium import webdriver
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

import pandas as pd

import time
from datetime import datetime

import pickle

from typing import Dict, Tuple

if __name__ == '__main__':
    from utils import parse_show_name
else:
    from scrapers.utils import parse_show_name


def siskel_showtime_scrape() -> Tuple[
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

    # Pull up the Siskel's show calendar, which involves navigating to
    # the calendar page and then clicking the button/link titled
    # "Calendar".
    siskel_link = 'https://www.siskelfilmcenter.org/calendar'
    driver.get(siskel_link)
    calendar_link_xpath = '/html/body/div[1]/div[4]/div/section/div[2]/article/div/div/p/a'
    true_calendar_element = driver.find_element(By.XPATH, calendar_link_xpath)
    true_calendar_link = true_calendar_element.get_attribute('href')
    driver.get(true_calendar_link)
    # driver.find_element(By.XPATH, calendar_link_xpath).click()

    # Now at the actual calendar, we check for a working link to the
    # next month's page, by checking for a clickable "Next" button.
#
    next_month_button_element = None
    try:
        next_month_button_element = driver.find_element(By.ID, 
                                                    'ctl00_CPH1_EventCalendar_calNext')
    except:
        print("WARNING: Could not identify next month's calendar.")
        time.sleep(3)
    
    calendar_links = [true_calendar_link]

    if next_month_button_element:
        
        print("In the 'next month' branch!")
        driver.implicitly_wait(3)
        next_month_button_element.click()
        driver.implicitly_wait(3)
        calendar_links.append(driver.current_url)
        print(f'Appended to calendar_links: {driver.current_url}')
        print(driver.current_url)

        driver.get(true_calendar_link)

        # next_month_cal_link = next_month_button_element.get_attribute('href')
        # print(next_month_cal_link)
        # calendar_links.append(next_month_cal_link)

    # Initialize various dictionaries
    films_showtimes = {} # Tracks each film's showtimes

    film_showtimes_2_list = []
    
    film_details = {} # Tracks the runtime, release year, and director
    #                 # of each film, as given by their "MORE INFO"
    #                 # page.

    shows_films_release_yrs = {} # Tracks the release year of each film.

    siskel_series_dict = {} # Tracks the various series shown at the
    #                       # Siskel, which appear to be indicated by a
    #                       # colon in the show title.

    # To time the scrape, note the current time as its start.
    scrape_start = time.time()

    for cal_link in calendar_links:
        driver.get(cal_link)

        # For this calendar page, get the HTML text and create a
        # BeautifulSoup object from it.
        calendar_xpath = '//*[@id="ctl00_CPH1_EventCalendar_CalendarTable"]/tbody'
        calendar_text = driver.find_element(By.XPATH, calendar_xpath
                                            ).get_attribute('innerHTML')
        soup = BeautifulSoup(calendar_text, 'html.parser')

        # Form an iterable of all the calendar's days, by selecting such
        # elements from the Soup.
        calendar_days = soup.select('td.InsideDate')

        # Iterate through each of the calendar's days in order to collect
        # data on the shows' times and films.
        for day in calendar_days:

            # Iterate through this day's shows.
            days_films = day.select('div.Item')
            for film in days_films:

                # Get the show's name, and parse it into the names of the
                # screened film and series (if applicable.)
                show_name = film.select_one('div.Name').text

                show_name = show_name.replace('Ô', 'O')

                film_name, show_series_prepends = parse_show_name(show_name)
                # print(show_name, film_name, show_series_prepends, sep='\t||\t')

                # If this show is indeed part of a series, log the series'
                # name in a dictionary.
                if show_series_prepends:
                    primary_series = show_series_prepends[0]
                    series_prepends_str = ': '.join(show_series_prepends)
                    # print(primary_series, series_prepends_str, film_name, sep='\t||||\t')
                    if primary_series not in siskel_series_dict:
                        siskel_series_dict[primary_series] = [(film_name, series_prepends_str)]
                    else:
                        siskel_series_dict[primary_series].append([(film_name, series_prepends_str)])

                # Iterate through this film's showtimes that day
                films_showtimes_that_day = film.select('div.Time')
                for showtime in films_showtimes_that_day:
                    # Retrieve the string that indicates the showtime and
                    # parse it into a datetime object.
                    showtime_str = showtime.get('data-agl_date') + 'M'
                    showtime_datetime = datetime.strptime(showtime_str, '%m/%d/%y %I:%M %p')

                    # Add this showtime to a dictionary of them, using the
                    # film's name as the key:

                    # If this film hasn't yet had any showtimes logged,
                    # first retrieve a few of its production details from
                    # its "MORE INFO" page on the Siskel site.
                    if film_name not in films_showtimes:

                        # Before scraping this film's info, create this film's
                        # showtime list with this first showtime.
                        films_showtimes[film_name] = [showtime_datetime]

                        # Navigate to the film's "MORE INFO" page.
                        # link_to_details_page = film.select_one('a.agl-epgbutton').get('href')
                        link_to_details_page = film.select_one('a.ViewLink').get('href')
                        link_to_details_page = 'https://prod5.agileticketing.net/websales/pages/' + link_to_details_page
                        driver.get(link_to_details_page)

                        # Instantiate a dictionary for just this film's
                        # production details.
                        this_films_details = {
                            'Release Year': None,
                            'Director': None,
                        }

                        # Iterate through the production details shown on
                        # that page, taking only those named in the below
                        # 'if/elif' branches. At time of writing, these
                        # include release year, runtime, and director.
                        film_detail_elems = driver.find_elements(By.CSS_SELECTOR, 'span.PropValue')
                        for detail_elem in film_detail_elems:
                            if detail_elem.get_attribute('cpropname').strip() == 'Release Year':
                                film_release_yr = detail_elem.get_attribute('innerHTML')
                                this_films_details['Release Year'] = film_release_yr
                                
                            elif detail_elem.get_attribute('cpropname').strip() == 'Runtime':
                                film_runtime = detail_elem.get_attribute('innerHTML')
                                film_runtime = int(film_runtime)
                                this_films_details['Runtime'] = film_runtime
                            
                            elif detail_elem.get_attribute('cpropname').strip() == 'Director':
                                film_director = detail_elem.get_attribute('innerHTML')
                                this_films_details['Director'] = film_director
                            
                        film_details[film_name] = this_films_details

                        # print(f'{film_name} added first-time. Details: {this_films_details}')

                    else:
                        films_showtimes[film_name].append(showtime_datetime)

                    showtime_2_record_dict = {
                            'Title': film_name,
                            'Year': film_details[film_name]['Release Year'],
                            'Director': film_details[film_name]['Director'],
                            'Showtime': showtime_datetime,
                        }
                    film_showtimes_2_list.append(showtime_2_record_dict)


    # # (For debugging/feedback) Print the various dictionaries.
    # print('',
    #       siskel_series_dict,
    #       films_showtimes,
    #       film_details,
    #       sep='\n\n')

    # Form a dataframe from the dictionary of the scraped films' details.
    film_details_df = pd.DataFrame.from_dict(film_details, orient='index').reset_index()
    film_details_df.rename(columns={'index': 'Title'}, inplace=True)
    film_details_df.to_csv('data/csv/siskel/siskel_inferior_show_info.csv', index=False)
    film_details_df.to_pickle('data/pkl/siskel/siskel_inferior_show_info.pkl')
 
    # Save to file the dictionaries of showtimes and production info.
    with open('data/pkl/siskel/siskel_showtimes_dict.pkl', 'wb') as file:
        pickle.dump(films_showtimes, file)

    with open('data/pkl/siskel/siskel_inferior_show_info_dict.pkl', 'wb') as file:
        pickle.dump(film_details, file)

    # Create a dataframe of the new showtimes dataset (in testing.)
    film_showtimes_2_df = pd.DataFrame(film_showtimes_2_list)
    film_showtimes_2_df['Showtime_Date'] = film_showtimes_2_df['Showtime'].dt.date
    film_showtimes_2_df['Showtime_Time'] = film_showtimes_2_df['Showtime'].dt.time

    # Save the new showtimes dataset.
    film_showtimes_2_df.to_csv(f'data/csv/siskel/siskel_showtimes_2.csv', index=False)
    film_showtimes_2_df.to_pickle(f'data/pkl/siskel/siskel_showtimes_2.pkl')

    # Note and print the runtime of the scrape.
    scrape_runtime = time.time() - scrape_start
    scrape_runtime = round(scrape_runtime)
    runtime_min = scrape_runtime // 60
    runtime_sec = scrape_runtime % 60
    scrape_runtime_str = f'{runtime_min} m {runtime_sec} s'
    print(f'\nRuntime of this Siskel scrape: {scrape_runtime_str}')

    # Quit and close the driver, to conclude.
    driver.quit()

    return films_showtimes, film_details_df

if __name__ == '__main__':

    # Run the Siskel scrape
    showtime_dict, inferior_info_df = siskel_showtime_scrape()

    # # Print previews of the scraped output:
    
    # Showtimes
    for movie, showtime_list in list(showtime_dict.items())[:5]:
        print(movie)
        for showtime in showtime_list:
            print(f'\t{showtime}')
        print()
    
    # A separator
    print('\n' + '-'*80 + '\n')

    # Show info
    print(inferior_info_df.head(), '\n')

