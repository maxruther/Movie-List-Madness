import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import time
from bs4 import BeautifulSoup
import re

import pandas as pd


# Driver setup
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Chrome(options)

cr_page_link = 'https://www.metacritic.com/movie/star-trek-into-darkness/critic-reviews/'
driver.get(cr_page_link)

trouble_cr = '/html/body/div[1]/div/div/div[2]/div[1]/div[1]/section/div[4]/div[42]/div'
review_text = driver.find_element(By.XPATH, trouble_cr)

soup = BeautifulSoup(review_text.get_attribute('innerHTML'), 'html.parser')

def get_cr_data_element(element_name: str, the_soup: BeautifulSoup, css_select_str: str) -> str:
    element_selection = soup.select(css_select_str)

    if len(element_selection) != 1:
        raise Exception(f"PARSE ERROR - {element_name.upper()}: More than one \
                        {element_name} value found for this critic's review.")

    element = element_selection[0].text.strip()
    # print(element)

    return element


publication = get_cr_data_element('publication', soup,
                                  'a.c-siteReviewHeader_publicationName')
rev_score = get_cr_data_element('review_score', soup,
                                'div.c-siteReviewScore:not(.c-siteReviewScore_background)')
date_written = get_cr_data_element('date_written', soup,
                                'div.c-siteReviewHeader_reviewDate')
rev_snippet = get_cr_data_element('review_snippet', soup, 
                                'div.c-siteReview_quote')
critic_name = get_cr_data_element('critic_name', soup,
                                'a.c-siteReview_criticName')

print(publication, rev_score, date_written, rev_snippet, critic_name,
      sep='\n')

# soup = BeautifulSoup(driver.page_source, 'html.parser')
# for EachPubl in soup.select('a[class*=c-siteReviewHeader_publicationName]'):
#     print(EachPubl.text.strip())


driver.close()




"""SCRATCH CODE FROM PREVIOUS DRAFT OF 'metacritic_cr_scrape.py' 
# # Retrieve the various desired data from the review's Soup, 
# # using the method just defined.
# publication = get_cr_data_element('publication', soup,
#                                 'a.c-siteReviewHeader_publicationName')
# score = get_cr_data_element('review_score', soup,
#                             'div.c-siteReviewScore:not(.c-siteReviewScore_background)')
# date_written = get_cr_data_element('date_written', soup,
#                                 'div.c-siteReviewHeader_reviewDate')
# snippet = get_cr_data_element('review_snippet', soup, 
#                                 'div.c-siteReview_quote')
# critic = get_cr_data_element('critic_name', soup,
#                                 '.c-siteReview_criticName')

# # From the critic's name, removing the prefix 'By ' if present, 
# # as it tends to be.
# if critic:
#     if critic[:3] == 'By ':
#         critic = critic[3:]

# # Write this critic review's line of data to the adhoc text 
# # file, to log it.
# adhoc_cr_file.write(f'{cr_counter},"{film_title}",' \
#                     + f'{publication},{score},{critic},' \
#                         + f'{snippet},{date_written}\n')
# cr_counter += 1

# # Create a dictionary from this critic review's data, then add
# # it to the list that eventually forms the final dataset.
# cr_dict = {'Film': film_title, 
#            'Publication': publication,
#            'Score': score, 
#            'Critic': critic, 
#            'Snippet': snippet,
#            'Date Written': date_written}
"""

"""
# # Isolated link - For test runs.
thelma_link_entry = df.loc[0]['Metacritic Page Suffix']
thelma_cr_link = 'https://www.metacritic.com' + thelma_link_entry + 'critic-reviews/'
print(thelma_cr_link)

thelma_title = df.loc[0]['Film']
print(thelma_title)

driver.get(thelma_cr_link)
"""