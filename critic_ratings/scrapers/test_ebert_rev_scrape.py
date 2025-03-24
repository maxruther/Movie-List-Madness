import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from bs4 import BeautifulSoup

import pandas as pd

import re

# # Driver setup
# options = webdriver.ChromeOptions()
# options.add_argument('--ignore-certificate-errors')
# options.add_argument('--ignore-ssl-errors')
# driver = webdriver.Chrome(options)

# driver.get('https://www.rogerebert.com/reviews')

# with open('data/test_ebert_rev_page.pkl', 'wb') as file:
#     pickle.dump(driver.page_source, file)

rev_page = None
with open('data/test_ebert_rev_page.pkl', 'rb') as file:
    rev_page = pickle.load(file)

rev_soup = BeautifulSoup(rev_page, 'html.parser')

movie_tiles = rev_soup.select('a.image-hover.cursor-pointer.relative.rounded.flex.flex-col.justify-end')
for movie_tile in movie_tiles:
    title = movie_tile.select_one('h3.text-2xl.z-10.mt-4.inline').text.strip()

    filled_star_box_elem = movie_tile.select_one('img.h-5.filled')

    if filled_star_box_elem:
        filled_star_box_elem_class_tags = filled_star_box_elem.get('class')
        star_rating = float(filled_star_box_elem_class_tags[-1].replace('star', ''))/10
        print(title, star_rating, sep='\t')

# genre_elem_class = 'px-2 sm:px-3 mb-4 text-xs montserrat-700 py-[4px] sm:py-2 border border-primary-gold rounded text-primary-gold sm:text-[13px] uppercase transition-colors hover:bg-primary-gold hover:text-white'

# other_genre_elem_class = "px-2 sm:px-3 text-xs montserrat-700 py-[4px] sm:py-2 border border-primary-gold rounded text-primary-gold sm:text-[13px] uppercase transition-colors hover:bg-primary-gold hover:text-white"
# # genre_elem_class = genre_elem_class.replace(':', '\:').replace(' ', '.')
# # print(genre_elem_class)

# for tag in other_genre_elem_class.split(' '):
#     if tag not in genre_elem_class.split(' '):
#         print(tag)

# for tag in genre_elem_class.split(' '):
#     if tag not in other_genre_elem_class.split(' '):
#         print(tag)



# movie_page_html = None
# with open('data/test_ebert_scrape.pkl', 'rb') as file:
#     movie_page_html = pickle.load(file)

# movie_page_soup = BeautifulSoup(movie_page_html, 'html.parser')

# genre_elem_class = 'mb-4.hover\:bg-primary-gold'
# genre_elements = movie_page_soup.select('a.' + genre_elem_class)

# # genre_elements = None

# if genre_elements:
#     for elem in genre_elements:
#         print(elem.text)


# movie_page_html = None
# with open('data/test_ebert_scrape.pkl', 'rb') as file:
#     movie_page_html = pickle.load(file)

# movie_page_soup = BeautifulSoup(movie_page_html, 'html.parser')

# li_elements = movie_page_soup.select('li.mb-2.sm\:mb-4')

# for elem in li_elements:
#     if 'Director' in elem.text:
#         print(elem.text)



# li_elements = None
# try:
#     li_elements = WebDriverWait(driver, timeout=5).until(lambda d: d.find_element(By.CSS_SELECTOR, 'li.mb-2.sm:mb-4'))
# except:
#     print("No 'li' elements found (for Director parsing)")

# if li_elements:
#     dir_elem = None
#     for elem in li_elements:
#         if 'Director' in elem.text:
#             print(elem.text)