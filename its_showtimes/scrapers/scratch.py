from selenium import webdriver
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

import time
from datetime import datetime

import pickle
import re

import pandas as pd

if __name__ == '__main__':
    from utils import parse_show_name
else:
    from scrapers.utils import parse_show_name


# Set up the Selenium Chromium driver
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.page_load_strategy = 'eager'
driver = webdriver.Chrome(options)
driver.implicitly_wait(5)

# link = 'https://www.siskelfilmcenter.org/dr-strangelove-ntl'
link = 'https://www.siskelfilmcenter.org/schrader-evening'
driver.get(link)

film_details_html = driver.page_source
film_details_soup = BeautifulSoup(film_details_html, 'html.parser')

# description = None
# desc_elem_xpath = '/html/body/div[1]/div[5]/div/section/div[2]/article/div/div[2]/p[1]'
# desc_elem = driver.find_element(By.XPATH, desc_elem_xpath)
# if desc_elem:
#     description = desc_elem.text.strip()
#     print("Found 'desc_elem' by XPATH!")
#     print(description)

description = None
main_content_elem = film_details_soup.select_one('div.main-container.container')
if main_content_elem:
    print("Found 'div.main-container.container'")
    summary_text_elem = main_content_elem.select_one('div.field--type-text-with-summary')
    if summary_text_elem:
        print("Found 'div.field--type-text-with-summary'")
        desc_elem = summary_text_elem.select_one('p')
        if desc_elem:
            print("Found first 'p'")
            description = desc_elem.text.strip()
            print("National Theatre Live: DR. STRANGELOVE", description, sep='\n')