import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from bs4 import BeautifulSoup

import pandas as pd

import re


# Driver setup
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.page_load_strategy = 'eager'

driver = webdriver.Chrome(options=options)


review_pg_3_5_and_4_stars = 'https://www.rogerebert.com/reviews?_rating_filter=35%2C40'
review_pg_4_stars = 'https://www.rogerebert.com/reviews?_rating_filter=40%2C40'

# reviews_page = review_pg_4_stars
reviews_page = review_pg_3_5_and_4_stars


driver.get(reviews_page)
soup = BeautifulSoup(driver.page_source, 'html.parser')


movie_tiles = soup.select('a.image-hover.cursor-pointer.relative.rounded.flex.flex-col.justify-end')

movie_dict_list = []

tv_show_list = []

for movie_tile in movie_tiles:
# for movie_tile in list(movie_tiles)[:5]:

    link = movie_tile.get('href')
    title = movie_tile.select_one('h3.text-2xl.z-10.mt-4.inline').text.strip()
    reviewer = movie_tile.select_one('div.montserrat-500.mt-2.text-meta-grey.text-sm').text.strip()

    if 'tv-review' in link:
        tv_show_list.append((title, link))

    rating = None

    filled_star_box_elem = movie_tile.select_one('img.h-5.filled')
    if filled_star_box_elem:
        filled_star_box_elem_class_tags = filled_star_box_elem.get('class')
        rating = float(filled_star_box_elem_class_tags[-1].replace('star', ''))/10
        print(title, rating, sep='\t')

    driver.get(link)

    more_details = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.CSS_SELECTOR, 'div.mt-4.text-label-grey.font-heading-sans.text-sm'))

    details_list = [deet.strip() for deet in more_details.text.split('‧')]

    runtime, mpa_rating, year = None, None, None

    runtime_pattern = r'^(\d*) min(?:ute)?s?$'
    yr_pattern = r'^(\d{4})$'

    for detail in details_list:
        if re.search(runtime_pattern, detail):
            runtime = re.search(runtime_pattern, detail).group(1)
        elif re.search(yr_pattern, detail):
            year = re.search(yr_pattern, detail).group(1)
        elif detail in ['R', 'PG-13', 'PG', 'G']:
            mpa_rating = detail


    director = None

    li_elements = None
    try:
        li_elements = WebDriverWait(driver, timeout=3).until(lambda d: d.find_elements(By.CSS_SELECTOR, 'li.mb-2.sm\:mb-4'))
    except:
        print("No 'li' elements found (for Director parsing)")

    if li_elements:
        dir_elem = None
        for elem in li_elements:
            if 'Director' in elem.text:
                director_elem_list = elem.text.split('\n')
                director = ', '.join(director_elem_list[1:])


    genre = None

    genre_elements = None
    try:
        genre_elements = WebDriverWait(driver, timeout=3).until(lambda d: d.find_elements(By.CSS_SELECTOR, 'a.mb-4.hover\:bg-primary-gold'))
    except:
        print("No 'a' elements found (for Genre parsing)")
    
    if genre_elements:
        for elem in genre_elements:
            genre = elem.text.strip()
        
    
    movie_dict = {
        'Title': title,
        'Release Year': year,
        'Director': director,
        'Rating': rating,
        'Reviewer': reviewer,
        'Runtime': runtime,
        'Genre': genre,
        'MPA Rating': mpa_rating,
        'Review Page Link': link,
    }


    movie_dict_list.append(movie_dict)

movie_df = pd.DataFrame(movie_dict_list)
movie_df.to_csv('data/scraped/ebert_radar.csv', index=False)
movie_df.to_pickle('data/scraped/ebert_radar.pkl')
print(movie_df)
print(tv_show_list)


driver.quit()