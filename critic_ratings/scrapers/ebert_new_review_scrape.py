from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

import pandas as pd


# Driver setup
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
driver = webdriver.Chrome(options)

four_star_reviews_page = 'https://www.rogerebert.com/reviews?_rating_filter=40%2C40'

driver.get(four_star_reviews_page)
soup = BeautifulSoup(driver.page_source, 'html.parser')


movie_tiles = soup.select('a.image-hover.cursor-pointer.relative.rounded.flex.flex-col.justify-end')

movie_dict_list = []

for movie_tile in movie_tiles:
# for movie_tile in list(movie_tiles)[:3]:
    # print(movie_tile.text.strip())

    link = movie_tile.get('href')
    title = movie_tile.select_one('h3.text-2xl.z-10.mt-4.inline').text.strip()
    reviewer = movie_tile.select_one('div.montserrat-500.mt-2.text-meta-grey.text-sm').text.strip()

    movie_dict = {
        'Title': title,
        'Link': link,
        'Reviewer': reviewer,
    }

    driver.get(link)
    review_soup = BeautifulSoup(driver.page_source, 'html.parser')

    more_details = review_soup.select_one('div.mt-4.text-label-grey.font-heading-sans.text-sm')

    print(more_details.text.strip())

    movie_dict_list.append(movie_dict)

movie_df = pd.DataFrame(movie_dict_list)
movie_df.to_csv('data/scraped/ebert_fourstar_movies.csv', index=False)
print(movie_df)



driver.quit()