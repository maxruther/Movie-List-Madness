import time

from selenium import webdriver
from selenium.webdriver.common.by import By

import re
from bs4 import BeautifulSoup

import pandas as pd


def sign_in_to_lb(user: str, pw: str):
    """ Creates a Google Chrome Selenium webdriver, signs it into Letterboxd with
    the given user and pass, then returns that signed-in webdriver."""

    # Set up the Selenium driver.
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options)
    
    # Navigate the driver to the letterboxd homepage.
    driver.get("https://letterboxd.com/")

    # Click the sign-in button, which presents the entry forms for user and pass.
    click_signin_xpath = '//*[@id="header"]/section/div[1]/div/nav/ul/li[1]/a'
    driver.find_element(By.XPATH, click_signin_xpath).click()

    # Enter the username
    username = driver.find_element(By.ID, 'username')
    username.send_keys(user)

    # Enter the pass
    password = driver.find_element(By.ID, 'password')
    password.send_keys(pw)

    # Submit the credentials to log in.
    submit_creds_xpath = '//*[@id="signin"]/fieldset/div/div[4]/div[1]/input'
    driver.find_element(By.XPATH, submit_creds_xpath).click()

    # Optional delay (for dev's reference, to see whether sign-in was successful. 
    time.sleep(3)

    # Return the signed-in driver.
    return driver


def lb_scrape_friends_ratings(lb_creds: list[str],
                              film_links: list[str], 
                            #   driver: webdriver, 
                              test_n_films: int = 0,
                              output_parentdir='letterboxd',
                              ) -> pd.DataFrame:
    
    # Unpack the creds which were read in from file.
    user, password, user_url = lb_creds

    driver = sign_in_to_lb(user, password)

    # If this is a test run, only run this scrape for the first films.
    # Also, create a suffix of '_test' for the names of any saved files.
    filename_suffix_test = ''
    if test_n_films:
        if len(film_links) >= test_n_films:
            film_links = film_links[:test_n_films]
    
        filename_suffix_test = '_test'

    output_filename = f'lb_friends_ratings_{user}{filename_suffix_test}'

        
    # (For the dev's reference) time the imminent scraping.
    scrape_start = time.time()

    # # If the parameter 'testing' is true and sufficiently low, limit the list of links
    # # to just the first three (for testing purposes.)
    # if testing and len(film_links) >= 3:
    #     film_links = film_links[:3]

    # Initialize list that will hold each film's dictionary of friend ratings.
    friend_ratings_dict_list = []

    for link in film_links:
        # Navigate the driver to the film link.
        driver.get(link)

        # From that page, retrieve the element detailing the film's title and year.
        film_title_xpath = '//*[@id="html"]/head/meta[7]'
        film_title_and_yr = driver.find_element(By.XPATH, film_title_xpath).get_attribute('content')

        # Parse the film's title and year from the retrieved string comprised of both.
        pattern = r'(^.+\S)\s+\((\d{4})\)$'
        film_title, film_year = re.search(pattern, film_title_and_yr).groups()

        # From that same film page, retrieve all 'Activity from Friends' elements. These
        # often contain ratings, the primary subject of this scraper.
        friend_activity_xpath = '//*[@id="film-page-wrapper"]/div[2]/section[3]/ul/li[contains(concat(" ", @class, " "), " -rated ")]'
        friend_activity_elements = driver.find_elements(By.XPATH, friend_activity_xpath)

        # # (For the dev's reference) print the film's title, year, and link.
        # print('\n---------------------------------',
        #     film_title, film_year, link, '\n', sep='\n')

        # Initialize this film's dictionary of friend ratings. Each friend's rating
        # of that film will be added to the dictionary as a new pair.
        friend_ratings_dict = {
            'title': film_title,
            'year': film_year,
            'link': link
            }
        
        # These films' dictionaries are iteratively so completed and added to a 
        # list, which ultimately forms the final dataframe.

        # Retrieving a rating from each friend activity element, if available.
        for i in friend_activity_elements:

            # Create a BeautifulSoup object from the element's html text.
            friend_activity_html_str = i.get_attribute('innerHTML')
            soup = BeautifulSoup(friend_activity_html_str, features='html.parser')

            # Parse the friend's name
            friend_name = soup.find('span', {'class': re.compile('avatar')}).img['alt']

            # Parse the friend's rating, and then convert it from stars to a numeral.
            friend_rating = soup.find('span', {'class': re.compile('rated-')}).text
            # Initialize the numeric rating to the count of full stars.
            numeric_rating = friend_rating.count('\u2605')
            # If there is a half-star, add 0.5 to that.
            if '\u00BD' in friend_rating:
                numeric_rating += 0.5

            # # (For the dev's reference) print the friend's name, 
            # # numeric rating, and star rating (for the dev's reference.)
            # print(friend_name, numeric_rating, friend_rating.strip(), 
            #     sep='\n', end='\n\n')

            friend_ratings_dict[friend_name] = numeric_rating
        
        # Add that film's dictionary of friend ratings to the list.
        friend_ratings_dict_list.append(friend_ratings_dict)
        print(f"Grabbed elements for {film_title_and_yr}")

        # # (For the dev's reference) print an acknowledgment that this
        # # film was processed.
        # print(f'Processed: {film_title} ({film_year})')

    # Create a dataframe from the list of dictionaries representing 
    # friends' ratings.
    friend_ratings_df = pd.DataFrame(friend_ratings_dict_list)

    # Save that dataframe to pkl and csv files, then return it.
    friend_ratings_df.to_csv(f'data/csv/{output_parentdir}/{output_filename}.csv', index=False)
    friend_ratings_df.to_pickle(f'data/pkl/{output_parentdir}/{output_filename}.pkl')

    
    # (For the dev's reference) print the runtime of the scrape.
    scrape_runtime = time.time() - scrape_start
    scrape_runtime = round(scrape_runtime)
    runtime_min = scrape_runtime // 60
    runtime_sec = scrape_runtime % 60
    scrape_runtime_str = f'{runtime_min} m {runtime_sec} s'
    print(f'\nRuntime of this scrape: {scrape_runtime_str}')


    # Close the Selenium driver to conclude.
    driver.close()

    return friend_ratings_df


if __name__ == "__main__":

    # For the Letterboxd user whose friends' reactions (to shared 
    # watches) are of interest, specify a file in which that user's
    # credentials can be found.
    sensitive_file = 'C:/Users/maxru/eclipse-workspace/movie_list_dvlp/lb.txt'

    # Specify creds and sign into Letterboxd. ('user_url' is the segment of the
    # letterboxd url that points to the user's page.)
    with open(sensitive_file, 'r') as file:
        lb_creds = file.read().split()
    user_url = lb_creds[2]

    # Read in the list of letterboxd film links (as scraped by 'lb_scrape_diary.py'.)
    lb_diary_df = pd.read_csv(f'data/csv/letterboxd/lb_diary_{user_url}.csv')
    lb_diary_links = lb_diary_df['Letterboxd Link'].values
    

    # Call this script's method to scrape that users' friends' ratings
    # (of shared watches.)
    # lb_friends_ratings_df = get_friends_ratings(lb_diary_links, driver)
    lb_friends_ratings_df = lb_scrape_friends_ratings(lb_creds,
                                                      lb_diary_links,
                                                    #   test_n_films=3,
                                                      )

    # # (For the dev's reference) print the dataframe of the user's friends' ratings.
    print('Scraped ratings from friends on Letterboxd:', 
          lb_friends_ratings_df,
          sep='\n\n')
