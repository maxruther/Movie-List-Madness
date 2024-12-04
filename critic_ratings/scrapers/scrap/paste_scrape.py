import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import tqdm
import pickle
import re
import datetime
import html
import ssl

# --- ignore ssl certificate ---
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/98.0.4758.82',
    }

def scrape_metacritic_paste_page():
    url = "https://www.metacritic.com/publication/paste-magazine/?sort-options=date"

    webpage = requests.get(url, headers=headers).text
    # print(webpage)

    soup = BeautifulSoup(webpage, "html.parser")

    reviews = soup.find_all("div", {"class": "c-siteReview g-bg-gray10 u-grid g-outer-spacing-bottom-large"})

    print(reviews)

scrape_metacritic_paste_page()


#     for link in links:
#         webpage = requests.get(link).text
#         # print("is this thing on")
#         # print(webpage)
#         soup = BeautifulSoup(webpage, "html.parser")

#         table_names = []
#         all_movies = soup.find_all("div", {"class": "review-stack--info"})
#         for movie in all_movies:
#             print(movie)
#             print(movie.find_all('a')[0].text)

#         print('\n')


#         all_movies = soup('figure', {'class': 'movie review'})
        
#         for movie in all_movies:
#             url = movie.a.get('href')
#             title = movie.find_all('a')[1].text
#             stars = len(movie.find_all('i', {'class': 'icon-star-full'})) + 0.5 * len(
#                 movie.find_all('i', {'class': 'icon-star-half'}))
        
#             try:
#                 year = movie.find('span', {'class': 'release-year'}).text[1:-1]
#             except:
#                 year = ''
        
#             review_list.append([title, stars, year, url])

#     df = pd.DataFrame(review_list, columns=['Title', 'EbertStars', 'Year', 'URL'])
#     return df


# review_df = scrape_ebert_review_page()
# print(review_df)
# #
# # print(review_df.shape)
# # print(review_df.dtypes)
# # print(review_df.head())
# # print(review_df.tail())
