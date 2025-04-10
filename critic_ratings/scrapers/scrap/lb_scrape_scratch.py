import pandas as pd
import numpy as np
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup

import time


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


# driver = sign_in_to_lb('yoyoyodaboy', '')

# # Set up the Selenium driver.
# options = webdriver.ChromeOptions()
# options.add_argument('--ignore-certificate-errors')
# options.add_argument('--ignore-ssl-errors')
# # options.page_load_strategy = 'eager'
# options.page_load_strategy = 'none'
# driver = webdriver.Chrome(options)

# link = 'https://letterboxd.com//film/the-peoples-joker/'

links = [
    'https://letterboxd.com//film/the-peoples-joker/',
    'https://letterboxd.com/film/persepolis/',   
]

friend_ratings_dict_list = []

for link in links:

    driver.get(link)

    friend_activity_section_css = 'section.section.activity-from-friends'
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, friend_activity_section_css)
                )
        )
    except TimeoutException:
        print(f"WARNING: No 'friend activity' element loaded.\nLink: {link}")


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
        
        print(film_title, film_year, film_director, sep='\n', end='\n\n')


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
                numeric_rating = star_rating.count('\u2605')
                # If there is a half-star, add 0.5 to that.
                if '\u00BD' in star_rating:
                    numeric_rating += 0.5
                friend_rating = numeric_rating
                
            # print(friend_name, friend_rating, star_rating)
            friend_ratings_dict[friend_name] = numeric_rating
    
    friend_ratings_dict['Link'] = link

    friend_ratings_dict_list.append(friend_ratings_dict)

friend_ratings_df = pd.DataFrame(friend_ratings_dict_list)
print(friend_ratings_df.head())

    # # Parse the friend's name
    #         friend_name = soup.find('span', {'class': re.compile('avatar')}).img['alt']

    #         # Parse the friend's rating, and then convert it from stars to a numeral.
    #         friend_rating = soup.find('span', {'class': re.compile('rated-')}).text
    #         # Initialize the numeric rating to the count of full stars.
    #         numeric_rating = friend_rating.count('\u2605')
    #         # If there is a half-star, add 0.5 to that.
    #         if '\u00BD' in friend_rating:
    #             numeric_rating += 0.5

    #         # # (For the dev's reference) print the friend's name, 
    #         # # numeric rating, and star rating (for the dev's reference.)
    #         print(friend_name, numeric_rating, friend_rating.strip(), 
    #             sep='\n', end='\n\n')

            # friend_ratings_dict[friend_name] = numeric_rating


# input_filename = 'lb_friends_ratings_yoyoyodaboy'
# # input_filename = 'lb_friends_ratings_yoyoyodaboy_test'
# # input_filename = 'lb_diary_yoyoyodaboy'
# # input_filename = 'lb_diary_yoyoyodaboy_test'

# lb_user_url, scrape_type = None, None
# testing = False
# if input_filename[-5:] == '_test':
#     lb_user_url = input_filename.split('_')[-2]
#     scrape_type = '_'.join(input_filename.split('_')[:-2])
#     testing = True
# else:
#     lb_user_url = input_filename.split('_')[-1]
#     scrape_type = '_'.join(input_filename.split('_')[:-1])

# print(lb_user_url, scrape_type, testing)



# test_str = """Dog Man,Dog Man,1.0,1.0,2025,2025,Peter Hastings,Peter Hastings,1.0,1.0,/movie/dog-man/
# Presence,Presence,1.0,1.0,2025,2024,Steven Soderbergh,Steven Soderbergh,1.0,1.0,/movie/presence/
# Sly Lives! (aka The Burden of Black Genius),Sly Lives! (aka the Burden of Black Genius),1.0,1.0,2025,2025,Questlove,Questlove,1.0,1.0,/movie/sly-lives!-aka-the-burden-of-black-genius/
# Rose,Rose,1.0,1.0,2025,2021,Aurélie Saada,Aurélie Saada,1.0,1.0,/movie/rose/"""

# print(test_str.split('\n'))

# for record in test_str.split('\n'):
#     # print(record.split(','))
#     print('\nINSERT INTO mc_searchresults\nVALUES (', ', '.join([f'"{x}"' for x in record.split(',')]), ');')





# # Reading in user prudentials from file, to obscure them to github.
# with open('C:/Users/maxru/eclipse-workspace/movie_list_dvlp/lb.txt', 'r') as file:
#     user, password = file.read().split()
#     # print(file.read().split())
#     print(user, password)


# # Parsing a film's title and year from a string that contains both (as featured in
# # Letterboxd pages dedicated tot hsoe films.)
# pattern = r'(^.+\S)\s+\((\d{4})\)$'
# text = 'Janet (Planet)   (2023)'
# title, year = re.search(pattern, text).groups()
# print(title, year, sep='\n')

# # Retrieving a list of link strings from a 'lb_diary_df', which now also features
# # title and year.
# user_url = 'yoyoyodaboy'
# lb_diary_df = pd.read_csv(f'{user_url}_lb_diary_df.csv')
# print(lb_diary_df['Letterboxd Link'].values)
