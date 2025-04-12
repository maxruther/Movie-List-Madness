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

from utils import create_chromedriver, save_output_df_to_dirs, print_runtime_of_scrape


def sign_in_to_lb(
        user: str, 
        pw: str
        ) -> webdriver.Chrome:
    """ Creates a Google Chrome Selenium webdriver, signs it into Letterboxd with
    the given user and pass, then returns that signed-in webdriver."""

    # Set up the Selenium driver.
    driver = create_chromedriver('eager')
    # driver = create_chromedriver('none')
    
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
        ) -> pd.DataFrame:
    
    # Unpack the creds which were read in from file.
    user, password, user_url = lb_creds

    # Set output file's name and parent dir within the data/pkl and 
    # data/csv folders.
    output_filename = f'lb_friends_ratings_{user_url}'
    output_subdir = 'letterboxd'
    

    # Instantiate the webdriver and sign it into Letterboxd using the
    # given creds.
    driver = sign_in_to_lb(user, password)

    # Set limit on wait times for the driver's page loadings
    time_limit_for_stuck_driver = 23
    driver.command_executor.set_timeout(time_limit_for_stuck_driver)

    # Set a wait period, to let crucial page element load up.
    delay_for_friend_ratings_elem  = 9


    # # If this is a test run, only run this scrape for the first films.
    # # Also, create a suffix of '_test' for the names of any saved files.
    # if test_n_films:
    #     if len(film_links) >= test_n_films:
    #         film_links = film_links[:test_n_films]

    # filename_test_prefix = 'test_' if test_n_films else ''
    # output_filename = f'{filename_test_prefix}lb_friends_ratings_{user_url}'

    # (For the dev's reference) time the imminent scraping.
    scrape_start = time.time()

    # Initialize list that will hold each film's dictionary of friend ratings.
    friend_ratings_dict_list = []

    # # Iterate through the film links passed to this method.
    # If testing, only iterate through the first <test_n_films> films
    if test_n_films:
        film_links = list(film_links)[:test_n_films]
    for link in film_links:

        # # Navigate the driver to the film link.

        # Set the CSS selector of the 'Activity from friends' section.
        friend_activity_section_css = 'section.section.activity-from-friends'

        # Loop until the driver has 'got' the link. IME of using
        # Selenium with Letterboxd, the driver often hangs, possibly due
        # to the endlessly-repeating video ads. In this loop, if the
        # driver hangs too long, I quit the driver and start a new one.
        link_getted = 0
        while not link_getted:
            try:
                driver.get(link)

                # This link abbreviation is useful for identifying what
                # watched film is currently being processed.
                link_abbr = link.split('/')[-2]
                # print(f"\nI've driver.get'd this URL!: {link_abbr}")

                # I start a timer to help with distinguishing between
                # two timeout errors: that resulting from this process
                # failing to identify a 'Activity with friends' section
                # and 2) when the driver just gets stuck.
                wait_timer = time.time()

                # I tell the driver to wait for a bit, to give the
                # 'Activity from friends' section time to load. That
                # loading shouldn't take longer than 7 seconds, IME.
                WebDriverWait(driver, delay_for_friend_ratings_elem).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, friend_activity_section_css)
                        )
                )

                # print(f"I've driver.wait'd this URL!: {link_abbr}")
                
                # If the element has been identified, I indicate that
                # the driver was successful in navigating to this link.
                link_getted = 1

            except (TimeoutException, ReadTimeoutError) as e:
                wait_time = time.time() - wait_timer

                # If the wait time was similar in length to the time
                # limit that I set for the driver timeout, then I
                # consider the driver stuck, and reboot it.
                if wait_time > time_limit_for_stuck_driver - 3:
                    print("ERROR: The driver appears to have gotten stuck.")
                    print(e)

                    # I try to quit the 'stuck' driver. IME, it rarely
                    # succeeds in quitting, and never promptly.
                    try:
                        driver.quit()
                        print("Successfully quit the driver after error.")
                    except Exception as quit_error:
                        print(f"WARNING: QUIT ERROR after driver failed to get.")

                    # Whether the stuck driver successfully quits or
                    # not, I boot up a new one.
                    print("Starting a new driver to continue the scrape.")
                    driver = sign_in_to_lb(user, password)
                    driver.command_executor.set_timeout(time_limit_for_stuck_driver)
                else:
                    # If the period before timeout was short enough to
                    # indicate that the element simply wasn't there
                    # (which is to be expected of obscure films) then
                    # print a warning to indicate the absence.
                    print(f"WARNING: No 'activity from friends' element identified for link:\n{link_abbr}")

                    # Also, proceed to end the loop by indicating
                    # success in link navigation.
                    link_getted = 1
            

        # # Command the driver to stop loading the page, now that the
        # # desired element's presence (or absence) has been determined.
        # # (This is to avoid loading the ads that constantly repeat,
        # # which I suspect that might sometimes stall the process 
        # # indefinitely.)
        # driver.execute_script("window.stop();")
        # print(f"I've stopped loading this URL!: {link_abbr}\n")
        
        # From the page's HTML, create a BeautifulSoup object to parse
        # it.
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Identify the title, year, and director from the film's
        # section 'production-masthead', which to me resembles the 
        # page's title or a main header.
        film_header_elem = soup.select_one('section.production-masthead')

        # If this section element is found, parse it for the film's
        # title, year, and director.
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

        # Start this film's friend rating's record by defining a
        # dictionary with the film data scraped so far.
        friend_ratings_dict = {
                'Title': film_title,
                'Year': film_year,
                'Director': film_director,
                }
        
        # Attempt to select the 'Activity from friends' section.
        activity_from_friends_elem = soup.select_one('section.section.activity-from-friends')

        # If that section is successfully selected, parse it for each
        # rating given by a friend.
        if activity_from_friends_elem:
            friend_rating_elements = activity_from_friends_elem.select('li.-rated')

            # Iterate through each rating by a friend.
            for rating_elem in friend_rating_elements:

                # Parse the friend's name from the 'img' element.
                friend_name = None
                img_elem = rating_elem.select_one('img')
                if img_elem:
                    friend_name = img_elem.get('alt')
                
                # Parse the friend's rating from the 'rating' span
                # element.
                friend_rating = None
                star_rating_elem = rating_elem.select_one('span.rating')

                # If a rating was identified, translate it from star
                # characters to the decimal count of those stars.
                if star_rating_elem:
                    star_rating = star_rating_elem.text.strip()
                    friend_rating = star_rating.count('\u2605')
                    # If there is a half-star, add 0.5 to that.
                    if '\u00BD' in star_rating:
                        friend_rating += 0.5

                # Add this friend's rating to this film's dictionary
                # record, under the friend's name.    
                friend_ratings_dict[friend_name] = friend_rating

                # print(friend_name, friend_rating, star_rating)
        
        # Add the film page's link to the dictionary record.
        friend_ratings_dict['Link'] = link

        # Add this film's dictionary record to the greater list of them.
        friend_ratings_dict_list.append(friend_ratings_dict)


    # Create a dataframe from the list of dictionaries representing 
    # friends' ratings.
    friend_ratings_df = pd.DataFrame(friend_ratings_dict_list)

    # Save this dataframe to csv and pkl files.
    save_output_df_to_dirs(
        friend_ratings_df,
        test_n_films,
        output_filename,
        output_subdir,
    )

    # # Save that dataframe to pkl and csv files, then return it.
    # friend_ratings_df.to_csv(f'data/csv/{output_parentdir}/{output_filename}.csv', index=False)
    # friend_ratings_df.to_pickle(f'data/pkl/{output_parentdir}/{output_filename}.pkl')

    
    # (For the dev's reference) print the runtime of the scrape.
    print_runtime_of_scrape(scrape_start)

    # scrape_runtime = time.time() - scrape_start
    # scrape_runtime = round(scrape_runtime)
    # runtime_min = scrape_runtime // 60
    # runtime_sec = scrape_runtime % 60
    # scrape_runtime_str = f'{runtime_min} m {runtime_sec} s'
    # print(f'\nRuntime of this scrape: {scrape_runtime_str}')


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
                                                      test_n_films=15,
                                                      )

    # # (For the dev's reference) print the dataframe of the user's friends' ratings.
    print('Scraped ratings from friends on Letterboxd:', 
          lb_friends_ratings_df,
          sep='\n\n')
