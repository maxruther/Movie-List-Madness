from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from utils import create_chromedriver, save_output_df_to_dirs, add_new_data_to_existing, get_existing_df_if_exists

from bs4 import BeautifulSoup

import pandas as pd

import re

from os.path import exists

def ebert_scrape_new_reviews(
        test_n_films: int = 0,
        ) -> pd.DataFrame:
    
    # Set file's name and parent dir within the data/pkl and data/csv
    # folders.
    output_filename = 'ebert_recent_reviews'
    output_subdir = 'ebert'

    # Load the relevant data-scrape file if it exists (in pkl format).
    # Otherwise, instantiate an empty dataframe in its place.
    existing_df = get_existing_df_if_exists(
        output_filename,
        output_subdir,
        test_n_films
    )

    
    # Initialize lists that will store the data scraped for each film
    # review (into dictionaries.)
    movie_dict_list = []
    tv_show_list = []
    

    # Instantiate the webdriver
    driver = create_chromedriver()

    # Set links to RogerEbert.com's recent review page, filtered by two
    # different minimum star-ratings.
    review_pg_3_5_and_4_stars = 'https://www.rogerebert.com/reviews?_rating_filter=35%2C40'
    review_pg_4_stars = 'https://www.rogerebert.com/reviews?_rating_filter=40%2C40'

    # reviews_page = review_pg_4_stars
    reviews_page = review_pg_3_5_and_4_stars

    # Navigate to the recent review page and create a BeautifulSoup
    # object thereof, for parsing.
    driver.get(reviews_page)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    movie_tiles = soup.select('a.image-hover.cursor-pointer.relative.rounded.flex.flex-col.justify-end')

    if test_n_films:
        movie_tiles = list(movie_tiles)[:test_n_films]
    
    for movie_tile in movie_tiles:

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

        more_details = WebDriverWait(driver, timeout=3).until(
            lambda d: d.find_element(
                By.CSS_SELECTOR, 
                'div.mt-4.text-label-grey.font-heading-sans.text-sm'
                )
            )

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
            'Year': year,
            'Director': director,
            'Rating': rating,
            'Reviewer': reviewer,
            'Runtime': runtime,
            'Genre': genre,
            'MPA Rating': mpa_rating,
            'Review Page Link': link,
        }


        movie_dict_list.append(movie_dict)

    # Create a dataframe from the scraped movie review data.
    new_data_df = pd.DataFrame(movie_dict_list)

    # Combine this new data with that existing, to form the final
    # dataframe of scraped data.
    final_df = add_new_data_to_existing(new_data_df, existing_df)

    # Save this final dataframe to csv and pkl files.
    save_output_df_to_dirs(
        final_df,
        test_n_films,
        output_filename,
        output_subdir,
        )

    driver.quit()

    return final_df


if __name__ == '__main__':
    # recent_review_df = ebert_scrape_new_reviews(test_n_films=5)
    recent_review_df = ebert_scrape_new_reviews()

    print(recent_review_df.head(10))