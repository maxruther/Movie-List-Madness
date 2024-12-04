import time
from selenium import webdriver
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
import re

import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz


def scrape_mc_page_links(fr_df: pd.DataFrame,
                            driver: webdriver,
                            test_n_films: int = 0,
                            ) -> pd.DataFrame:
    """Return a dataframe of links to individual films' Metacritic
    pages, given a dataframe containing their titles and release years
    as well as a Chromium WebDriver object.
    
    This function also writes those links to file, in two forms:
        - 'mc_page_links.txt' - written as each link is scraped.
        - 'mc_page_links.csv' - only written once all scraping finishes.
    """

    # If this is a test run, only run this scrape for the first films.
    # Also, create a prefix of 'test_' for the names of any saved files.
    filename_prefix_test = ''
    if test_n_films:
        if len(fr_df) >= test_n_films:
            fr_df = fr_df[:test_n_films]

        filename_prefix_test = 'test_'

    df_filename = f'data/scraped/{filename_prefix_test}mc_page_links'
    
    # Open a file to write to, to save the links as they're each
    # scraped. This can be a helpful log when errors occur.
    adhoc_filename = f'{df_filename}.txt'
    adhoc_link_file = open(adhoc_filename, 'w')
    adhoc_link_file.write(',Film,Metacritic Page Suffix\n')

    # To form the index of this adhoc file, initialize a counter.
    link_counter = 0

    # Initialize a dictionary that will contain the links to the films'
    # dedicated pages on Metacritic. This dictionary will eventually 
    # form the final dataset.
    mc_page_links = {}

    # For each film record, search that film on Metacritic and record 
    # the link of the best-matching result. The match is based on the
    # similarities of the titles and release years.
    for index, film_record in fr_df.iterrows():

        # Assign the film's title, release year, and their concatenation to
        # dedicated variables.
        film_title = film_record['Title']
        film_year = film_record['Release Year']
        film_title_and_year = f'{film_title} ({film_year})'

        # The Metacritic search is conducted by creating a URL link of the
        # search. To create the URL segment that corresponds to the search
        # entry, punctuation is removed and spaces are replaced with '%20'.
        # (The Metacritic search doesn't acknowledge punctuation at all, per
        # my testing.)
        pattern = re.compile('[^a-zA-Z0-9\s]*')
        film_title_url_suffix = pattern.sub('', film_title)\
            .lower()\
                .replace(' ', '%20')

        # Submit a search URL ending with that segment to the driver, to run
        # that Metacritic search and get a page of its results.
        driver.get('https://www.metacritic.com/search/' + film_title_url_suffix)

        # Collect that page's results into an iterable, by identifying them
        # by a common XPath pattern.
        search_results_xpath = '//*[@id="__layout"]/div/div[2]/div[1]/div[2]/div[2]/div[@class="g-grid-container u-grid-columns"]'
        results = driver.find_elements(By.XPATH, search_results_xpath)

        # Instantiate a word vectorizer that will be used to calculate the
        # similarities between the search term and the results.
        vectorizer = CountVectorizer()

        # Initialize a dictionary where some such 'fuzzy' similarities will
        # be stored.
        top_results = {}

        # Iterate through each search result.
        for one_result in results:
            # Create a BeautifulSoup object from the result's HTML code, to
            # parse its data.
            soup = BeautifulSoup(one_result.get_attribute('innerHTML'), 'html.parser')

            # Parse the search result's link, title, and its type, which in
            # this context indicates the work's medium (e.g. movie, video game, 
            # or TV series, among others.)
            result_link = soup.find('a').get('href')
            result_title = soup.find('p', {'class': 'g-text-medium-fluid g-text-bold g-outer-spacing-bottom-small u-text-overflow-ellipsis'}).text.strip()
            result_type = soup.find('span', {'class': 'c-tagList_button g-text-xxxsmall'}).text.strip()
            
            # If the result isn't of type 'movie', then it's disregarded.
            if result_type != 'movie':
                continue
            
            # The release year of the result is also parsed.
            result_year = soup.find('span', {'class': 'u-text-uppercase'}).text.strip()

            # Similarities between the searched film title and the result
            # are computed, both cosine and 'fuzzy' ones. 
            vectors = vectorizer.fit_transform([film_title.lower(), result_title.lower()])
            cos_sim = cosine_similarity(vectors[0], vectors[1])[0][0]
            fuzzy_sim = fuzz.ratio(film_title.lower(), result_title.lower())

            # # (For the dev's reference: print a result's title, year,
            # # similarities, and result link.)
            # print(f'{result_title} ({result_year})\n\tCosine sim. = {cos_sim}\n\tFuzzy sim. = {fuzzy_sim}',
            #     result_link,  
            #     sep='\n', end='\n\n')
            
            # If the release year of the searched film matches that of a
            # result, that result is considered a top candidate. As
            # such, its similarities to the searched title (and its 
            # link) are stored in a dictionary for later comparison to 
            # the others.
            if result_year == film_year:
                top_results[result_title] = {'link': result_link, 
                                                        'fuzzy_sim': fuzzy_sim,
                                                        'cosine_sim': cos_sim}
        
        # With the results' examination now complete, the single-most
        # similar search result is chosen.
        if len(top_results) == 1:
            # If there is only one result with matching release year, then it is
            # decided as the chosen result.
            result_title, result_dict = top_results.popitem()
            mc_page_links[film_title_and_year] = result_dict['link']

            # # (For the dev's reference: print the result's title/header and
            # # its link.)
            # print(f'{result_title}')
            # for i in result_dict:
            #     print(f'\t{i}: {result_dict[i]}')
            
            # Write the index, film title & year, and the link of the chosen
            # result.
            adhoc_link_file.write(f'{link_counter},"{film_title_and_year}",{result_dict['link']}\n')
            link_counter += 1

        elif len(top_results) > 1:
            # If there are multiple results to decide from, then the one
            # with the highest 'fuzzy' similiarity to the searched title is
            # chosen.
            max_fuzzy_sim = 0
            maximally_fuzzy_res_dict = {}
            maximally_fuzzy_res_title = ''
            for result in top_results:
                if top_results[result]['fuzzy_sim'] > max_fuzzy_sim:
                    maximally_fuzzy_res_title = result
                    maximally_fuzzy_res_dict = top_results[result]
                    max_fuzzy_sim = top_results[result]['fuzzy_sim']
            mc_page_links[film_title_and_year] = maximally_fuzzy_res_dict['link']
            
            # # (For the dev's reference: print the title and link of the
            # # result with maximal similarity to the searched title.)
            # print(f'{maximally_fuzzy_res_title=}\n{maximally_fuzzy_res_dict.items()=}')
            # print(maximally_fuzzy_res_title)
            # for i in maximally_fuzzy_res_dict:
            #     print(f'\t{i}: {maximally_fuzzy_res_dict[i]}')
            
            # To conclude the processing of this film record, write the 
            # index, film title & year, and the link of the chosen result.
            adhoc_link_file.write(f'{link_counter},"{film_title_and_year}",{maximally_fuzzy_res_dict['link']}\n')
            link_counter += 1
        else:
            # If no results are identified for the film, print a warning.
            print("WARNING: No results found for queried film!\n",
                f'{film_title=}\t{result_title=}\n{film_year=}\t{result_year=}\n')
    
    # Close the adhoc file, now that writing is finished.
    adhoc_link_file.close()

    # Create a final dataframe from the above-generated dictionary of 
    # films and links (to their Metacritic 'Critic Review' pages.) 
    films, links = zip(*mc_page_links.items())
    mc_page_links_df = pd.DataFrame({'Film': films, 'Metacritic Page Suffix': links})

    # Save the final dataframe to a csv file.
    mc_page_links_df.to_csv(f'{df_filename}.csv', index=False)
    mc_page_links_df.to_pickle(f'{df_filename}.pkl')

    return mc_page_links_df


if __name__ == '__main__':
    
    # Specify the URL segment that leads to the page of the desired user.
    my_user_url = 'yoyoyodaboy'

    # Read in dataset that contains movie titles and release years.
    fr_df = pd.read_csv(f'data/scraped/lb_diary_{my_user_url}.csv')
    fr_df['Release Year'] = fr_df['Release Year'].astype(str) 

    # Set up the Selenium webdriver for Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    driver = webdriver.Chrome(options)

    # (For the dev's reference) time the imminent scraping.
    scrape_start = time.time()

    # Call method to search and scrape for the films' Metacritic pages.
    # mc_page_links_df = scrape_mc_page_links(fr_df, driver)
    mc_page_links_df = scrape_mc_page_links(fr_df, driver, test_n_films=3)

    # (For the dev's reference) print the runtime of the scrape.
    scrape_runtime = time.time() - scrape_start
    scrape_runtime = round(scrape_runtime)
    runtime_min = scrape_runtime // 60
    runtime_sec = scrape_runtime % 60
    scrape_runtime_str = f'{runtime_min} m {runtime_sec} s'
    print(f'\nRuntime of this scrape: {scrape_runtime_str}')

    # Close the ChromiumDriver
    driver.quit()

    # (For the dev's reference: print this final dataframe.)
    print(mc_page_links_df)

