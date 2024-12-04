import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import pickle

import re
from bs4 import BeautifulSoup

import pandas as pd

import time

# Set up the Selenium driver.
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
driver = webdriver.Chrome(options)

def get_letterboxd_cookies(method='sign in'):

    accepted_methods = ['sign in', 'load from file']
    if method not in accepted_methods:
        raise Exception('ERROR: Invalid entry for method parameter.')

    cookie_dict = None

    if method == 'load from file':
        with open('letterboxd_cookies.pickle', 'rb') as file:
            cookie_dict = pickle.load(file)
        
    elif method == 'sign in':
        driver.get("https://letterboxd.com/")
        # time.sleep(4)

        click_signin_xpath = '//*[@id="header"]/section/div[1]/div/nav/ul/li[1]/a'
        driver.find_element(By.XPATH, click_signin_xpath).click()

        username = driver.find_element(By.ID, 'username')
        username.send_keys('yoyoyodaboy')

        password = driver.find_element(By.ID, 'password')
        password.send_keys('BarnacleBoy135$@')

        submit_creds_xpath = '//*[@id="signin"]/fieldset/div/div[4]/div[1]/input'
        driver.find_element(By.XPATH, submit_creds_xpath).click()
        # WebDriverWait(driver, 5).until(
        #     EC.element_to_be_clickable(driver.find_element(By.XPATH, 
        #                                                 submit_creds_xpath))
        # ).click()

        time.sleep(3)

        cookie_dict = driver.get_cookies()

        with open('letterboxd_cookies.pickle', 'wb') as file:
            pickle.dump(cookie_dict, file)

    return cookie_dict    


letterboxd_cookies = get_letterboxd_cookies('sign in')

with open('all_my_film_links.pickle', 'rb') as file:
    all_my_film_links = pickle.load(file)

# for cookie in letterboxd_cookies:
#         driver.add_cookie(cookie)

movie_review_index = []
movie_review_dict_list = []

for film_link in all_my_film_links[:10]:
# for film_link in all_my_film_links:
    driver.get(film_link)

    movie_title_xpath = '//*[@id="html"]/head/meta[7]'
    movie_title = driver.find_element(By.XPATH, movie_title_xpath).get_attribute('content')
    # print(f'\n\n{movie_title}\n')

    movie_review_index.append(movie_title)

    friend_activity_xpath = '//*[@id="film-page-wrapper"]/div[2]/section[3]/ul/li[contains(concat(" ", @class, " "), " -rated ")]'
    friend_activity_elements = driver.find_elements(By.XPATH, friend_activity_xpath)

    print('\n\n' + film_link + '\n')

    movie_review_dict = {'link': film_link}


    for i in friend_activity_elements:
        reviewer_html_string = i.get_attribute('innerHTML')
        soup = BeautifulSoup(reviewer_html_string)
        span_elements = soup.find_all('span')

        reviewer_name = soup.find('span', {'class': re.compile('avatar')}).img['alt']
        print(reviewer_name)

        reviewer_rating = soup.find('span', {'class': re.compile('rated-')}).text
        numeric_rating = reviewer_rating.count('\u2605')
        if '\u00BD' in reviewer_rating:
            numeric_rating += 0.5
        print(numeric_rating)
        print(reviewer_rating)

        movie_review_dict[reviewer_name] = numeric_rating


        print('\n')


        # print(i.get_attribute('innerHTML'))

    movie_review_dict_list.append(movie_review_dict)
        
# print(movie_review_index[:2])
# print(movie_review_dict_list[:2])

movie_review_df = pd.DataFrame(movie_review_dict_list, index=movie_review_index)
movie_review_df.index.name = 'Film'

print(movie_review_df)
movie_review_df.to_pickle('LB_friends_ratings_df.pkl')
movie_review_df.to_csv('LB_friends_ratings_df.csv')

driver.close()