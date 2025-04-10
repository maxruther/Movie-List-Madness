import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib3.exceptions import ReadTimeoutError

import re
from bs4 import BeautifulSoup

import pandas as pd


def sign_in_to_lb(
        user: str, 
        pw: str
        ) -> webdriver.Chrome:
    """ Creates a Google Chrome Selenium webdriver, signs it into Letterboxd with
    the given user and pass, then returns that signed-in webdriver."""

    # Set up the Selenium driver.
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    # options.page_load_strategy = 'eager'
    options.page_load_strategy = 'none'
    driver = webdriver.Chrome(options)
    
    # Navigate the driver to the letterboxd homepage.
    driver.get("https://letterboxd.com/")

    click_signin_xpath = '//*[@id="header"]/section/div[1]/div/nav/ul/li[1]/a'
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, click_signin_xpath))
        )
    except:
        raise Exception("ERROR - 'sign_in_to_lb': Couldn't locate",
                        "'sign-in' button in time.")


    # Click the sign-in button, which presents the entry forms for user and pass.
    driver.find_element(By.XPATH, click_signin_xpath).click()

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'username'))
        )
    except:
        raise Exception("ERROR - 'sign_in_to_lb': Couldn't locate",
                        "'username' button in time.")


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


def lb_scrape_friends_ratings(
        lb_creds: list[str],
        film_links: list[str],
        test_n_films: int = 0,
        output_parentdir='letterboxd',
        ) -> pd.DataFrame:
    
    # Unpack the creds which were read in from file.
    user, password, user_url = lb_creds

    driver = sign_in_to_lb(user, password)

    # Set limit on wait times for the driver's page loadings
    time_limit_for_stuck_driver = 23
    driver.command_executor.set_timeout(time_limit_for_stuck_driver)

    # Set a wait period, to let crucial page element load up.
    delay_for_friend_ratings_elem  = 6


    # If this is a test run, only run this scrape for the first films.
    # Also, create a suffix of '_test' for the names of any saved files.
    if test_n_films:
        if len(film_links) >= test_n_films:
            film_links = film_links[:test_n_films]

    filename_test_prefix = 'test_' if test_n_films else ''
    output_filename = f'{filename_test_prefix}lb_friends_ratings_{user_url}'

    # (For the dev's reference) time the imminent scraping.
    scrape_start = time.time()

    # Initialize list that will hold each film's dictionary of friend ratings.
    friend_ratings_dict_list = []

    

    for link in film_links:
        # Navigate the driver to the film link.

        friend_activity_section_css = 'section.section.activity-from-friends'

        link_getted = 0
        while not link_getted:
            try:
                driver.get(link)

                link_abbr = link.split('/')[-2]
                print(f"\nI've driver.get'd this URL!: {link_abbr}")

                wait_timer = time.time()
                WebDriverWait(driver, delay_for_friend_ratings_elem).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, friend_activity_section_css)
                        )
                )

                print(f"I've driver.wait'd this URL!: {link_abbr}")
                
                link_getted = 1

            except (TimeoutException, ReadTimeoutError) as e:
                wait_time = time.time() - wait_timer
                if wait_time > time_limit_for_stuck_driver - 3:
                    print("ERROR: The driver failed to 'get' and 'wait'!")
                    print(e)
                    try:
                        driver.quit()
                        print("Successfully quit the driver after error!")
                    except Exception as quit_error:
                        print(f"WARNING: QUIT ERROR after driver failed to get.")
                    driver = sign_in_to_lb(user, password)
                    driver.command_executor.set_timeout(time_limit_for_stuck_driver)
                else:
                    print(f"WARNING: No 'activity from friends' element identified for link:\n{link_abbr}")
                    link_getted = 1
            
        # except TimeoutException:
        #     print(f"WARNING: No 'friend activity' element loaded.\nLink: {link}")

        print(f"I've waited after driver.get'ing this URL!: {link_abbr}")

        driver.execute_script("window.stop();")
        print(f"I've stopped loading this URL!: {link_abbr}\n")
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        film_header_elem = soup.select_one('section.production-masthead')

        film_title, film_year, film_director = None, None, None
        if film_header_elem:

            film_title = None
            film_title_elem = film_header_elem.select_one('h1')
            if film_title_elem:
                film_title = film_title_elem.text.strip()

            film_year = None
            film_year_elem = film_header_elem.select_one('div.releaseyear')
            if film_year_elem:
                film_year = film_year_elem.text.strip()

            film_director = None
            film_director_elem = film_header_elem.select_one('span.directorlist')
            if film_director_elem:
                film_director = ', '.join([x for x in film_director_elem.text.strip().split('\n') if x])
            
            # print(film_title, film_year, film_director, sep='\n', end='\n\n')


        friend_ratings_dict = {
                'Title': film_title,
                'Year': film_year,
                'Director': film_director,
                }
        
        activity_from_friends_elem = soup.select_one('section.section.activity-from-friends')

        if activity_from_friends_elem:
            friend_rating_elements = activity_from_friends_elem.select('li.-rated')

            for rating_elem in friend_rating_elements:

                friend_name = None
                img_elem = rating_elem.select_one('img')
                if img_elem:
                    friend_name = img_elem.get('alt')
                
                friend_rating = None
                star_rating_elem = rating_elem.select_one('span.rating')
                if star_rating_elem:
                    star_rating = star_rating_elem.text.strip()
                    friend_rating = star_rating.count('\u2605')
                    # If there is a half-star, add 0.5 to that.
                    if '\u00BD' in star_rating:
                        friend_rating += 0.5
                    
                # print(friend_name, friend_rating, star_rating)
                friend_ratings_dict[friend_name] = friend_rating
        
        friend_ratings_dict['Link'] = link

        friend_ratings_dict_list.append(friend_ratings_dict)

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
    lb_diary_df = pd.read_pickle(f'data/pkl/letterboxd/lb_diary_{user_url}.pkl')
    # lb_diary_df = pd.read_csv(f'data/csv/letterboxd/lb_diary_{user_url}.csv')
    lb_diary_links = lb_diary_df['LB_Film_Link'].values
    

    # Call this script's method to scrape that users' friends' ratings
    # (of shared watches.)
    # lb_friends_ratings_df = get_friends_ratings(lb_diary_links, driver)
    lb_friends_ratings_df = lb_scrape_friends_ratings(lb_creds,
                                                      lb_diary_links,
                                                    #   test_n_films=5,
                                                      )

    # # (For the dev's reference) print the dataframe of the user's friends' ratings.
    print('Scraped ratings from friends on Letterboxd:', 
          lb_friends_ratings_df,
          sep='\n\n')
