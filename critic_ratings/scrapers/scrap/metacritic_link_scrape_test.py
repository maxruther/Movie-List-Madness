from selenium import webdriver
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
import re

import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz

# Read in movie titles and years
fr_df = pd.read_csv('yoyo_lb_diary_df.csv')
fr_df['Release Year'] = fr_df['Release Year'].astype(str) 

# film_title_and_year = fr_df.iloc[9]['Film']

# Set up the Selenium webdriver for Chrome
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Chrome(options)

# Open or overwrite a file
adhoc_link_file = open('cr_link_scrape.txt', 'w')
adhoc_link_file.write(',Film,Metacritic Page Suffix\n')
link_counter = 0

critic_rating_links = {}

for index, film_record in fr_df.iterrows():
# for index, film_record in fr_df[:20].iterrows():
    film_title = film_record['Title']
    film_year = film_record['Release Year']
    film_title_and_year = f'{film_title} ({film_year})'

    pattern = re.compile('[^a-zA-Z0-9\s]*')
    film_title_url_suffix = pattern.sub('', film_title).lower().replace(' ', '%20')

    # Go to the website
    driver.get('https://www.metacritic.com/search/' + film_title_url_suffix)
    # driver.get('https://www.metacritic.com/search/' + 'tar')
    # film_title = 'Tar'
    # film_year = '2022'

    # one_search_result_xpath = '//*[@id="__layout"]/div/div[2]/div[1]/div[2]/div[2]/div[1]/a/div[2]'
    # one_result = driver.find_element(By.XPATH, one_search_result_xpath).get_attribute('innerHTML')

    # search_results_xpath = '//*[@id="__layout"]/div/div[2]/div[1]/div[2]/div[2]/div/a/div[@class="u-text-overflow-ellipsis"]'
    search_results_xpath = '//*[@id="__layout"]/div/div[2]/div[1]/div[2]/div[2]/div[@class="g-grid-container u-grid-columns"]'
    results = driver.find_elements(By.XPATH, search_results_xpath)
    vectorizer = CountVectorizer()

    best_results_fuzzy_sims = {}
    for one_result in results:
        soup = BeautifulSoup(one_result.get_attribute('innerHTML'), 'html.parser')
        result_link = soup.find('a').get('href')
        result_title = soup.find('p', {'class': 'g-text-medium-fluid g-text-bold g-outer-spacing-bottom-small u-text-overflow-ellipsis'}).text.strip()
        result_type = soup.find('span', {'class': 'c-tagList_button g-text-xxxsmall'}).text.strip()
        if result_type != 'movie':
            continue
        result_year = soup.find('span', {'class': 'u-text-uppercase'}).text.strip()

        vectors = vectorizer.fit_transform([film_title.lower(), result_title.lower()])
        cos_sim = cosine_similarity(vectors[0], vectors[1])[0][0]
        fuzzy_sim = fuzz.ratio(film_title.lower(), result_title.lower())

        # print(f'{result_title} ({result_year})\n\tCosine sim. = {cos_sim}\n\tFuzzy sim. = {fuzzy_sim}',
        #     result_link,  
        #     sep='\n', end='\n\n')
        
        if result_year == film_year:
            best_results_fuzzy_sims[result_title] = {'link': result_link, 
                                                     'fuzzy_sim': fuzzy_sim,
                                                     'cosine_sim': cos_sim}
    if len(best_results_fuzzy_sims) == 1:
        result_title, result_dict = best_results_fuzzy_sims.popitem()
        critic_rating_links[film_title_and_year] = result_dict['link']

        print(f'{result_title}')
        for i in result_dict:
            print(f'\t{i}: {result_dict[i]}')
        
        adhoc_link_file.write(f'{link_counter},"{film_title_and_year}",{result_dict['link']}\n')
        link_counter += 1

    elif len(best_results_fuzzy_sims) > 1:
        max_fuzzy_sim = 0
        maximally_fuzzy_res_dict = {}
        maximally_fuzzy_res_title = ''
        for result in best_results_fuzzy_sims:
            if best_results_fuzzy_sims[result]['fuzzy_sim'] > max_fuzzy_sim:
                maximally_fuzzy_res_title = result
                maximally_fuzzy_res_dict = best_results_fuzzy_sims[result]
                max_fuzzy_sim = best_results_fuzzy_sims[result]['fuzzy_sim']
        critic_rating_links[film_title_and_year] = maximally_fuzzy_res_dict['link']
        # print(f'{maximally_fuzzy_res_title=}\n{maximally_fuzzy_res_dict.items()=}')
        print(maximally_fuzzy_res_title)
        for i in maximally_fuzzy_res_dict:
            print(f'\t{i}: {maximally_fuzzy_res_dict[i]}')
        
        adhoc_link_file.write(f'{link_counter},"{film_title_and_year}",{maximally_fuzzy_res_dict['link']}\n')
        link_counter += 1
    else:
        print("ERROR: No results found for queried film!\n",
              f'{film_title=}\t{result_title=}\n{film_year=}\t{result_year=}\n')

# print(critic_rating_links.items())
adhoc_link_file.close()

films, links = zip(*critic_rating_links.items())
metacritic_cr_links_df = pd.DataFrame({'Film': films, 'Metacritic Page Suffix': links})

print(metacritic_cr_links_df)

metacritic_cr_links_df.to_csv('metacritic_cr_links.csv')

driver.close()

