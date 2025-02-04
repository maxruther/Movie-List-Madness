from selenium import webdriver
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

import pandas as pd

from select_text_from_soup import select_text_from_soup

import time
from datetime import datetime

import pickle

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Chrome(options)

# (For the dev's reference) time the imminent scraping.
scrape_start = time.time()

mb_calendar_link = 'https://musicboxtheatre.com/films-and-events'

driver.get(mb_calendar_link)

calendar_elem_xpath = '/html/body/div[1]/main/div/div[2]/div/div/div/div[2]'

calendar_text = driver.find_element(By.XPATH, calendar_elem_xpath).get_attribute('innerHTML')

with open('mb_calendar_text.pkl', 'wb') as file:
    pickle.dump(calendar_text, file)

soup = BeautifulSoup(calendar_text, 'html.parser')

# calendar_days = soup.select('div.Item')
# calendar_days = soup.select('td.InsideDate', limit=1)
calendar_days = soup.select('div.calendar-cell')

films_showtimes = {}
shows_films_release_yrs = {}

siskel_series_dict = {}

for day in calendar_days:

    day_num = day.text
    
    day_and_mon = day.select_one('span.d-md-none')
    print(day_and_mon)
    if day_and_mon:
        print(day_and_mon.text)

    year = day.select_one('span.d-none.d-lg-inline')
    print(year)
    if year:
        print(year.text)

driver.close()

# (For the dev's reference) print the runtime of the scrape.
scrape_runtime = time.time() - scrape_start
scrape_runtime = round(scrape_runtime)
runtime_min = scrape_runtime // 60
runtime_sec = scrape_runtime % 60
scrape_runtime_str = f'{runtime_min} m {runtime_sec} s'
print(f'\nRuntime of this scrape: {scrape_runtime_str}')