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


def scrape_eberts_review(num_pages=3):
    """
    Parses through webpage with list of movies and returns DataFrame.
    :num_pages = Number of pages to go through
    """
    # url = "https://www.rogerebert.com/reviews"
    url = "http://www.rogerebert.com/reviews?great_movies=0&no_stars=0&title=Cabin+in+the+Woods&filtersgreat_movies%5D%5B%5D=&filters%5Bno_stars%5D%5B%5D=&filters%5Bno_stars%5D%5B%5D=1&filters%5Btitle%5D=&filters%5Breviewers%5D=&filters%5Bgenres%5D=&page={}&sort%5Border%5D=newest"
    pages = list(range(1, num_pages))
    links = [url.format(i) for i in pages]

    review_list = list()

    for link in links:
        webpage = requests.get(link).text
        # print("is this thing on")
        # print(webpage)
        soup = BeautifulSoup(webpage, "html.parser")

        table_names = []
        all_movies = soup.find_all("div", {"class": "review-stack--info"})
        for movie in all_movies:
            # print(movie)
            print(movie.find_all('a')[0].text)

        print('\n')


        # all_movies = soup('figure', {'class': 'movie review'})
        #
        # for movie in all_movies:
        #     url = movie.a.get('href')
        #     title = movie.find_all('a')[1].text
        #     stars = len(movie.find_all('i', {'class': 'icon-star-full'})) + 0.5 * len(
        #         movie.find_all('i', {'class': 'icon-star-half'}))
        #
        #     try:
        #         year = movie.find('span', {'class': 'release-year'}).text[1:-1]
        #     except:
        #         year = ''
        #
        #     review_list.append([title, stars, year, url])

    df = pd.DataFrame(review_list, columns=['Title', 'EbertStars', 'Year', 'URL'])
    return df


review_df = scrape_eberts_review()
#
# print(review_df.shape)
# print(review_df.dtypes)
# print(review_df.head())
# print(review_df.tail())
