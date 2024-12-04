from selenium import webdriver
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

import pandas as pd

from select_text_from_soup import select_text_from_soup

import time


def scrape_mc_critic_reviews(mc_link_df: pd.DataFrame,
                             selenium_webdriver: webdriver.Chrome,
                             test_n_films: int = 0):

    # If this is a test run, only run this scrape for the first films.
    # Also, create a prefix of 'test_' for the names of any saved files.
    filename_prefix_test = ''
    if test_n_films:
        if len(mc_link_df) >= test_n_films:
            mc_link_df = mc_link_df[:test_n_films]
    
        filename_prefix_test = 'test_'
    
    output_filename = f'data/scraped/{filename_prefix_test}mc_cr'

    # Initialize a list that will hold the dictionaries of every 
    # individual critic review. This list will ultimately form the final
    # dataset.
    cr_dict_list = []

    # Open a file to write to, to save the reviews as they're scraped, 
    # line-by-line. This can be a helpful log when errors occur.
    # If this is a test run, add a filename prefix of 'test_'.
    adhoc_filename = f'{output_filename}.txt'
    adhoc_cr_file = open(adhoc_filename,
                         'w',
                         encoding='utf-8')

    # Write a header into the first line of this adhoc critic review 
    # file.
    adhoc_cr_file.write(',Film,Publication,Author,Snippet,Date Written\n')
    # A counter will form the index of the critics' reviews.
    cr_counter = 0

    # Iterrate through each record of the Metacritic movie link df
    for index, film_record in mc_link_df.iterrows():

        # Log the film's title and URL segment (pointing to its 
        # Metacritic page.)
        film_title = film_record['Film']
        film_link_entry = film_record['Metacritic Page Suffix']

        # From that URL segment, form the URL that leads to that film's 
        # 'Critic Reviews' page. Then navigate the webdriver to that 
        # page.
        film_cr_link = f'https://www.metacritic.com' + film_link_entry \
            + 'critic-reviews/'
        
        selenium_webdriver.get(film_cr_link)

        # Using the webdriver, collect all elements containing critic 
        # reviews into an iterable.
        reviews_xpath = '//*[@id="__layout"]/div/div[2]/div[1]/' \
            + 'div[1]/section/div[4]/div/div'
        
        review_texts = selenium_webdriver.find_elements(By.XPATH, 
                                                        reviews_xpath)

        # # (For the dev's reference) Print the index (+1) and the 
        # film's title.
        """print(f'\n\nMovie #{index+1}: {film_title}')"""

        # Iterate through each critic review of this film.
        for review_text in review_texts:

            # Create a BeautifulSoup object from this review.
            soup = BeautifulSoup(review_text.get_attribute('innerHTML'), 
                                'html.parser')
            
            # Define a dictionary of the various data elements sought
            # and their corresponding CSS selector strings.
            css_sel_strs = {
                'Publication': 'a.c-siteReviewHeader_publicationName',
                'Score': 'div.c-siteReviewScore' \
                    + ':not(.c-siteReviewScore_background)',
                'Critic': '.c-siteReview_criticName',
                'Snippet': 'div.c-siteReview_quote',
                'Date Written': 'div.c-siteReviewHeader_reviewDate',
            }

            # Initialize this critic review's data dictionary as only
            # containing the film's title.
            cr_dict = {'Film': film_title}

            # For each of desired attribute and corresponding 
            # CSS-selectorstring, retrieve and enter this critic 
            # review's data into the dictionary. 
            for attr, css_str in css_sel_strs.items():
                value = select_text_from_soup(attr, soup, css_str)
                cr_dict.update({attr: value})

            # If the 'Critic' value is prefixed with the prhase 'By ' 
            # (as it tends to be) then remove that prefix.
            critic_name = cr_dict['Critic']
            if len(critic_name) >= 3:
                if critic_name[:3] == 'By ':
                    cr_dict['Critic'] = critic_name[3:]
            
            
            # Add this critic review's data dictionary to their list.
            cr_dict_list.append(cr_dict)

    # Close the adhoc file and the webdriver, to start finishing up.
    adhoc_cr_file.close()
    selenium_webdriver.close()
    selenium_webdriver.quit()

    # Form a dataframe from the list of critic review dictionaries.
    metacritic_cr_master_df = pd.DataFrame(cr_dict_list)

    # Save the final dataframe of critic reviews to a csv file.
    metacritic_cr_master_df.to_csv(f'{output_filename}.csv', index=False)
    metacritic_cr_master_df.to_pickle(f'{output_filename}.pkl')

if __name__ == '__main__':

    # Driver setup
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')

    driver = webdriver.Chrome(options)

    # Read in the relative paths of films' Metacritic pages 
    mc_link_df = pd.read_csv('data/scraped/mc_page_links.csv')

    # (For the dev's reference) time the imminent scraping.
    scrape_start = time.time()

    # Run this script's method to scrape the individual metacritic 
    # reviews of the films featured in the given metacritic movie link
    # dataset.
    # scrape_mc_critic_reviews(mc_link_df, driver)
    scrape_mc_critic_reviews(mc_link_df, driver, test_n_films=3)

    # (For the dev's reference) print the runtime of the scrape.
    scrape_runtime = time.time() - scrape_start
    scrape_runtime = round(scrape_runtime)
    runtime_min = scrape_runtime // 60
    runtime_sec = scrape_runtime % 60
    scrape_runtime_str = f'{runtime_min} m {runtime_sec} s'
    print(f'\nRuntime of this scrape: {scrape_runtime_str}')
