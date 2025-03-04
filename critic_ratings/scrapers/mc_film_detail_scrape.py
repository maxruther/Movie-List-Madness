import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
import re

import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz

import os


def mc_film_detail_scrape(fr_df: pd.DataFrame,
                            driver: webdriver,
                            test_n_films: int = 0,
                            output_filename='mc_film_details',
                            adding_to_existing_df=True,
                            ) -> pd.DataFrame:

    # If this is a test run, only run this scrape for the first films.
    # Also, create a prefix of 'test_' for the names of any saved files.
    filename_suffix_test = ''
    if test_n_films:
        if len(fr_df) >= test_n_films:
            fr_df = fr_df[:test_n_films]

        filename_suffix_test = '_test'

    df_filename = f'data/scraped/{output_filename}{filename_suffix_test}'

    # Check for an existing file. If one exists, this scraper just adds to it.
    mcs_df = pd.DataFrame()
    mcs_res_log_df = pd.DataFrame()
    
    if adding_to_existing_df:
        if os.path.exists(f'{df_filename}.pkl'):
            mcs_df = pd.read_pickle(f'{df_filename}.pkl')

        if os.path.exists(f'{df_filename}_search_results_log.pkl'):
            mcs_res_log_df = pd.read_pickle(f'{df_filename}_search_results_log.pkl')

    
    # # Open a file to write to, to save the links as they're each
    # # scraped. This can be a helpful log when errors occur.
    # adhoc_filename = f'{df_filename}.txt'
    # adhoc_link_file = open(adhoc_filename, 'w')
    # adhoc_link_file.write(',Film,Metacritic Page Suffix\n')

    # To form the index of this adhoc file, initialize a counter.
    link_counter = 0

    # Initialize a dictionary that will contain the links to the films'
    # dedicated pages on Metacritic. This dictionary will eventually 
    # form the final dataset.
    mc_page_links = {}

    mc_search_results_log = []

    prod_detail_dict_list = []

    # For each film record, search that film on Metacritic and record 
    # the link of the best-matching result. The match is based on the
    # similarities of the titles and release years.
    for index, film_record in fr_df.iterrows():

        # Assign the film's title, release year, and their concatenation to
        # dedicated variables.
        film_title = film_record['Title']
        
        film_year = film_record['Release Year']

        # Check for bogus year entry, which Siskel submissions sometimes have.
        # example_str = '2017-2024'
        year_range_pattern = r"\d{4}–\d{4}"
        if re.search(year_range_pattern, film_year):
            continue

        film_title_and_year = f'{film_title} ({film_year})'

        print(f'\nNext scrape:\t{film_title} ({film_year})')
        if not mcs_df.empty:
            
            # print(mcs_df.loc[(mcs_df['Title Searched'] == film_title) & (mcs_df['Year Searched'] == film_year)])
            if not mcs_res_log_df.loc[(mcs_res_log_df['Title Searched'] == film_title) & (mcs_res_log_df['Year Searched'] == film_year)].empty:
                print(f'{film_title} ({film_year}) already scraped. Skipping...')
                continue

        if 'Director' in fr_df.columns:
            film_director = film_record['Director']
            if pd.isna(film_director):
                film_director = None
        else:
            film_director = None

        # The Metacritic search is conducted by creating a URL link of the
        # search. To create the URL segment that corresponds to the search
        # entry, punctuation is removed and spaces are replaced with '%20'.
        # (The Metacritic search doesn't acknowledge punctuation at all, per
        # my testing.)
        film_title = film_title.replace('Ô', 'O')
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
        results_htmls = [result.get_attribute('innerHTML') for result in results]

        # Instantiate a word vectorizer that will be used to calculate the
        # similarities between the search term and the results.
        vectorizer = CountVectorizer()

        # Initialize a dictionary where some such 'fuzzy' similarities will
        # be stored.
        top_results = {}

        chosen_link = ''

        # Iterate through each search result.
        perfect_result_not_found = True
        # for one_result in results:
        for result_html in results_htmls:
            if perfect_result_not_found:

                # Create a BeautifulSoup object from the result's HTML code, to
                # parse its data.
                soup = BeautifulSoup(result_html, 'html.parser')

                # Parse the search result's link, title, and its type, which in
                # this context indicates the work's medium (e.g. movie, video game, 
                # or TV series, among others.)
                result_link = soup.find('a').get('href')
                result_title = soup.find('p', {'class': 'g-text-medium-fluid g-text-bold g-outer-spacing-bottom-small u-text-overflow-ellipsis'}).text.strip()
                result_type = soup.find('span', {'class': 'c-tagList_button g-text-xxxsmall'}).text.strip()

                # If the result isn't of type 'movie', then it's disregarded.
                if result_type != 'movie':
                    continue

                result_year = soup.find('span', {'class': 'u-text-uppercase'}).text.strip()

                # Similarities between the searched film title and the result
                # are computed, both cosine and 'fuzzy' ones. 
                vectors = vectorizer.fit_transform([film_title.lower(), result_title.lower()])
                title_cos_sim = cosine_similarity(vectors[0], vectors[1])[0][0]
                title_cos_sim = round(title_cos_sim, 3)
                title_fuzzy_sim = fuzz.ratio(film_title.lower(), result_title.lower())
                title_fuzzy_sim = round(title_fuzzy_sim / 100, 3)

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
                if abs(int(result_year) - int(film_year)) <= 1:
                # if result_year == film_year:
                    result_director, director_fuzzy_sim, director_cos_sim = None, None, None
                    if film_director:

                        # Navigate to result film's dedicated page on Metacritic.
                        driver.get('https://www.metacritic.com' + result_link)
                        soup = BeautifulSoup(driver.page_source, 'html.parser')

                        # Find the director(s) of the film on the page.
                        director_elems_parent = soup.select_one('div.c-crewList.g-inner-spacing-bottom-small.c-productDetails_staff_directors')
                        if director_elems_parent:
                            director_elems = director_elems_parent.select('a.c-crewList_link.u-text-underline')
                            result_director = ', '.join([director_elem.text.strip(' ,\n\t') for director_elem in director_elems])

                            # Calculate similarities of the director strings for the
                            # result and searched film.
                            print(f'{film_title} {film_director} {result_director}')
                            director_vectors = vectorizer.fit_transform([film_director.lower(), result_director.lower()])
                            director_cos_sim = cosine_similarity(director_vectors[0], director_vectors[1])[0][0]
                            director_cos_sim = round(director_cos_sim, 3)

                            director_fuzzy_sim = fuzz.ratio(film_director.lower(), result_director.lower())
                            director_fuzzy_sim = round(director_fuzzy_sim / 100, 3)

                            print(f'{film_title} ({film_year}) Director similarities:',
                                f'{film_director}\t{result_director}',
                                f'Fuzzy sim. = {director_fuzzy_sim}\nCosine sim. = {director_cos_sim}',
                                sep='\n', end='\n\n')
                    
                    search_result_dict = {
                        'Title Searched': film_title,
                        'Title Result': result_title,
                        'Titles Fuzzy Sim': title_fuzzy_sim,
                        'Titles Cosine Sim': title_cos_sim,
                        'Year Searched': film_year,
                        'Year Result': result_year,
                        'Director Searched': film_director,
                        'Director Result': result_director,
                        'Directors Fuzzy Sim': director_fuzzy_sim,
                        'Directors Cosine Sim': director_cos_sim,
                        'Link': result_link,
                    }

                    # Store this search result's data in this film's
                    # dictionary of top candidates.
                    top_results[result_title] = search_result_dict

                    # Store this search result's data in the log of all movie
                    # results with showing this film's year.
                    mc_search_results_log.append(search_result_dict)

                    # If the search result's title and director are (cosine) similar
                    # at 1, then it is chosen as the match and the remaining search
                    # results are skipped.
                    if title_cos_sim == 1 and director_cos_sim == 1:
                        perfect_result_not_found = False
        
        # With the results' examination now complete, the single-most
        # similar search result is chosen.
        if len(top_results) == 1:
            # If there is only one result with matching release year, then it is
            # decided as the chosen result.
            result_title, result_dict = top_results.popitem()
            mc_page_links[film_title_and_year] = result_dict['Link']

            # If the result's title and director are (cosine) similar enough to those of the searched film, then it is chosen as the match.
            if result_dict['Titles Cosine Sim'] == 1:
                chosen_link = result_dict['Link']
            elif result_dict['Titles Cosine Sim'] < 1:
                if result_dict['Directors Cosine Sim'] >= 0.5:
                    chosen_link = result_dict['Link']
                else:
                    print("\nWARNING: No suitably matched result for the queried film! There were some results that showed the same year, but the cosine similarities between the titles and directors were too low to indicate a match.\n",
                    f'{film_title=}\n{film_year=}\n')


            # # (For the dev's reference: print the result's title/header and
            # # its link.)
            # print(f'{result_title}')
            # for i in result_dict:
            #     print(f'\t{i}: {result_dict[i]}')
            
            # # Write the index, film title & year, and the link of the chosen
            # # result.
            # adhoc_link_file.write(f'{link_counter},"{film_title_and_year}",{result_dict['Link']}\n')
            # link_counter += 1

        elif len(top_results) > 1:
            # If there are multiple results to decide from, then the one
            # with the highest 'fuzzy' similiarity to the searched title is
            # chosen.
            max_fuzzy_sim = 0
            maximally_fuzzy_res_dict = {}
            for result in top_results:
                if top_results[result]['Titles Fuzzy Sim'] > max_fuzzy_sim:
                    maximally_fuzzy_res_dict = top_results[result]
                    max_fuzzy_sim = top_results[result]['Titles Fuzzy Sim']

            mc_page_links[film_title_and_year] = maximally_fuzzy_res_dict['Link']

            # if test_n_films:
            #     print(f'\n\n{film_title_and_year}\n{top_results}\n')
            
            # If the result's title and director are (cosine) similar enough to those of the searched film, then it is chosen as the match.
            if maximally_fuzzy_res_dict['Titles Cosine Sim'] == 1:
                chosen_link = maximally_fuzzy_res_dict['Link']
            elif maximally_fuzzy_res_dict['Titles Cosine Sim'] < 1:
                if maximally_fuzzy_res_dict['Directors Cosine Sim']:
                    if maximally_fuzzy_res_dict['Directors Cosine Sim'] >= 0.5:
                        chosen_link = maximally_fuzzy_res_dict['Link']
            else:
                print("\nWARNING: No suitably matched result for the queried film! There were some results that showed the same year, but the cosine similarities between the titles and directors were too low to indicate a match.\n",
                f'{film_title=}\t{film_director=}\n{maximally_fuzzy_res_dict['Title Result']}\t{maximally_fuzzy_res_dict['Director Result']=}\n')

            
            # # (For the dev's reference: print the title and link of the
            # # result with maximal similarity to the searched title.)
            # print(f'{maximally_fuzzy_res_title=}\n{maximally_fuzzy_res_dict.items()=}')
            # print(maximally_fuzzy_res_title)
            # for i in maximally_fuzzy_res_dict:
            #     print(f'\t{i}: {maximally_fuzzy_res_dict[i]}')
            
            # # To conclude the processing of this film record, write the 
            # # index, film title & year, and the link of the chosen result.
            # adhoc_link_file.write(f'{link_counter},"{film_title_and_year}",{maximally_fuzzy_res_dict['Link']}\n')
            # link_counter += 1
        else:
            # If no results are identified for the film, print a warning.
            print("\nWARNING: No movie results show a matching year for the queried film!\n",
                f'{film_title=}\n{film_year=}\n')
            
            mc_search_results_log.append({
                    'Title Searched': film_title,
                    'Year Searched': film_year,
                })

            
        if chosen_link:

            prod_detail_dict = {
                'Title': film_title,
                'Year': film_year,
                'Link': chosen_link,
            }


            # Navigate to the film's Metacritic page.
            driver.get('https://www.metacritic.com' + chosen_link)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            ### FINDING AND ADDING FILM DETAILS FROM THE METACRITIC PAGE

            # Metascore
            review_score_elems = soup.select('div.c-productScoreInfo.u-clearfix')
            for elem in review_score_elems:
                review_type = elem.get('data-testid')
                if review_type == 'critic-score-info':
                    metascore = elem.select_one('div.c-siteReviewScore').text.strip()
                    if metascore == 'tbd':
                        metascore = None
                    else:
                        metascore = float(metascore) / 100
                    prod_detail_dict['Metascore'] = metascore
                    # print(film_title, 'Metascore:', metascore)

            # Summary
            summary_element = soup.select_one('span.c-productDetails_description.g-text-xsmall')
            if summary_element:
                summary = summary_element.text.strip()
                prod_detail_dict['Summary'] = summary
                # print(film_title, summary)

            # Director(s)
            directors_element = soup.select_one('div.c-crewList.g-inner-spacing-bottom-small.c-productDetails_staff_directors').select('a.c-crewList_link.u-text-underline')
            if directors_element:
                directors_str = ' '.join([director.text.strip() for director in directors_element])
                prod_detail_dict['Directors'] = directors_str
                # print(film_title, directors_str)

            # Writer(s)
            writers_detail_element = soup.select_one('div.c-crewList.g-inner-spacing-bottom-small.c-productDetails_staff_writers')
            # writers_element = soup.select_one('div.c-crewList.g-inner-spacing-bottom-small.c-productDetails_staff_writers').select('a.c-crewList_link.u-text-underline')
            if writers_detail_element:
                writer_entries_element = writers_detail_element.select('a.c-crewList_link.u-text-underline')
                writers_str = ' '.join([writer.text.strip() for writer in writer_entries_element])
                prod_detail_dict['Writers'] = writers_str
                # print(film_title, writers_str)


            # Runtime and (US theatrical) release date
            prod_detail_elems = soup.select('div.c-movieDetails_sectionContainer')
            for elem in prod_detail_elems:
                prod_detail_type = elem.select_one('span.g-text-bold').text.strip()

                if prod_detail_type == 'Duration':
                    runtime_str = elem.select_one('span.g-outer-spacing-left-medium-fluid').text.strip()
                
                    # print(film_title, film_year, runtime_str,
                    #     sep='\t', end='\n\n')
                    
                    if 'h' not in runtime_str:
                        runtime_str = '0 h ' + runtime_str
                    if 'm' not in runtime_str:
                        runtime_str = runtime_str + ' 0 m'
                    
                    runtime_str = runtime_str.replace('h', '').replace('m', '')
                    runtime_hrs, runtime_mins = [int(i) for i in runtime_str.split()]
                    runtime_in_minutes = runtime_hrs * 60 + runtime_mins

                    prod_detail_dict['Runtime'] = runtime_in_minutes
                    # print(film_title, runtime_in_minutes)

                if prod_detail_type == 'Release Date':
                    release_date = elem.select_one('span.g-outer-spacing-left-medium-fluid').text.strip()
                    release_date = datetime.strptime(release_date, '%b %d, %Y')
                    release_date = datetime.strftime(release_date, '%Y-%m-%d')
                    prod_detail_dict['Release Date'] = release_date
                    # print(film_title, release_date)
        
            prod_detail_dict_list.append(prod_detail_dict)
    
    # print(prod_detail_df)

    # If there is an existing dataframe, concatenate the new records to it.
    if not mcs_df.empty:
        new_mcs_records = pd.DataFrame(prod_detail_dict_list)
        mcs_df = pd.concat([mcs_df, new_mcs_records], ignore_index=True)
    # Otherwise, create a new dataframe from the records.
    else:
        mcs_df = pd.DataFrame(prod_detail_dict_list)
    
    # Save the production details to file, from a dataframe.
    mcs_df.to_csv(f'{df_filename}.csv', index=False)
    mcs_df.to_pickle(f'{df_filename}.pkl')

    if not mcs_res_log_df.empty:
        new_res_log_records = pd.DataFrame(mc_search_results_log)
        mcs_res_log_df = pd.concat([mcs_res_log_df, new_res_log_records], ignore_index=True)
    else:
        mcs_res_log_df = pd.DataFrame(mc_search_results_log)

    # Save the search results log to file, from a dataframe.    
    mcs_res_log_df.to_csv(f'{df_filename}_search_results_log.csv', index=False)
    mcs_res_log_df.to_pickle(f'{df_filename}_search_results_log.pkl')

    # # Save the search results log to file, from a dataframe.
    # mc_search_results_log_df = pd.DataFrame(mc_search_results_log)
    # mc_search_results_log_df.to_csv(f'{df_filename}_search_results_log.csv', index=False)
    # mc_search_results_log_df.to_pickle(f'{df_filename}_search_results_log.pkl')
    
    # # # Close the adhoc file, now that writing is finished.
    # # adhoc_link_file.close()

    # Save the production details to file, from a dataframe.
    # prod_detail_df = pd.DataFrame(prod_detail_dict_list)
    # prod_detail_df.to_csv(f'{df_filename}.csv', index=False)
    # prod_detail_df.to_pickle(f'{df_filename}.pkl')

    return mcs_df


if __name__ == '__main__':
    
    # Specify the URL segment that leads to the page of the desired user.
    my_user_url = 'yoyoyodaboy'

    # Read in dataset that contains movie titles and release years.
    fr_df = pd.read_csv(f'data/scraped/lb_diary_{my_user_url}.csv')
    fr_df['Release Year'] = fr_df['Release Year'].astype(str) 
    
    # ALTERNATE FILE: Read in dataset with titles, release years, and directors.
    fr_df = pd.read_csv(f'data\showtimes\showtime_master_titles_yrs.csv')

    # Set up the Selenium webdriver for Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    driver = webdriver.Chrome(options)

    # (For the dev's reference) time the imminent scraping.
    scrape_start = time.time()

    # Call method to search and scrape for the films' Metacritic pages.
    # mc_page_links_df = scrape_mc_page_links(fr_df, driver)
    prod_detail_df = mc_film_detail_scrape(fr_df, driver, test_n_films=20)

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
    print(prod_detail_df)
