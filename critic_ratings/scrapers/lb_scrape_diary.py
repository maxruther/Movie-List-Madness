import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import pickle
import csv

import pandas as pd


def get_users_diary_links(user_url: str, 
                          driver: webdriver.Chrome,
                          output_parentdir='letterboxd') -> list[str]:
    # Navigate to user's film diary page.
    driver.get(f"https://letterboxd.com/{user_url}/films/diary/")

    # From that page, retrieve the diary's page count.
    diary_pages_xpath = '//*[@id="content"]/div/section[2]/div[2]/div[3]/ul/li/a'
    diary_page_elems = driver.find_elements(By.XPATH, diary_pages_xpath)
    diary_page_count = diary_page_elems[-1].get_attribute('text')

    # Initialize lists where the films' titles, release years, and 
    # letterboxd links will be stored.
    all_film_links = []
    all_film_titles = []
    all_film_release_yrs = []

    # Scrape each page of the film diary for that information.
    for i in range(1, int(diary_page_count) + 1):
        # Navigate to the i-th diary page.
        diary_page_link = f'https://letterboxd.com/{user_url}/films/diary/page/{str(i)}/'
        driver.get(diary_page_link)

        # Retrieve the letterboxd links to all films on this diary page. This involves
        # removing the username from those links.
        this_pages_links = [film_entry.get_attribute('href').replace(f'/{user_url}', '') 
                            for film_entry in 
                            driver.find_elements(By.XPATH,
                                                    '//*[@id="diary-table"]/tbody/tr/td/h3/a')]
        
        # Retrieve the titles of all the films on this diary page.
        this_pages_film_titles = [film_entry.text for film_entry in driver.find_elements(By.XPATH, '//*[@id="diary-table"]/tbody/tr/td/h3/a')]

        # Retrieve their release years, too.
        this_pages_film_release_yrs = [year_item.text for year_item in driver.find_elements(By.XPATH, '//*[@id="diary-table"]/tbody/tr/td[4]')]

        # Add this diary page's links, titles, and release years to the corresponding
        # master lists.
        all_film_links += this_pages_links
        all_film_titles += this_pages_film_titles
        all_film_release_yrs += this_pages_film_release_yrs

    # From the film diary lists just generated, create a dataframe, then return it.
    letterboxd_diary_df = pd.DataFrame({'Title': all_film_titles,
                  'Release Year': all_film_release_yrs,
                  'Letterboxd Link': all_film_links})
    
    # Write the dataframe of the user's film diary links to a csv file.
    letterboxd_diary_df.to_csv(f'data/csv/{output_parentdir}/lb_diary_{my_user_url}.csv', index=False)
    letterboxd_diary_df.to_pickle(f'data/pkl/{output_parentdir}/lb_diary_{my_user_url}.pkl')
    
    return letterboxd_diary_df


if __name__ == '__main__':

    # Set up Selenium driver
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options)

    # Specify the URL segment that leads to the page of the desired user.
    my_user_url = 'yoyoyodaboy'

    # Retrieve the links in the letterboxd user's film diary, through scraping.
    users_lb_diary_df = get_users_diary_links(my_user_url, driver)

    # Print the dataframe (for the developer to check at a glance.)
    print('\nScraped links of Letterboxd diary entries:',
          users_lb_diary_df,
          sep='\n\n')

    # Close the driver to conclude.
    driver.close()
