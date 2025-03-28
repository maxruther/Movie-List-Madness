import time

from selenium import webdriver

import re

import pandas as pd

import os

from mc_utilities.mc_info_scrape import mc_info_scrape
from mc_utilities.mc_review_scrape import mc_review_scrape
from mc_utilities.mc_get_films_link import mc_get_films_link


def combine_and_save_data(new_data: list[dict[str: str]],
                            existing_df: pd.DataFrame,
                            output_filepath: str,
                            ):

    # If there is an existing dataframe, concatenate the new records to it.
    if not existing_df.empty:
        new_data_df = pd.DataFrame(new_data)
        existing_df = pd.concat([existing_df, new_data_df], ignore_index=True)
    # Otherwise, create a new dataframe from the records.
    else:
        existing_df = pd.DataFrame(new_data)
    
    

    # Save the final dataframe of critic reviews to a csv file.
    existing_df.to_csv(f'data/csv/{output_filepath}.csv', index=False)
    existing_df.to_pickle(f'data/pkl/{output_filepath}.pkl')


def mc_search_and_scrape(
        target_film_df: pd.DataFrame,
        test_n_films: int = 0,
        # cr_filename: str = 'mc_reviews',
        # info_filename: str = 'mc_info',
        # searchresults_filename: str = 'mc_searchresults',
        output_filename: str = 'searchnscrape',
        output_parentdir: str = 'metacritic',
        adding_to_existing_df: bool = True,
        consult_master_files: bool = False,
        ) -> pd.DataFrame:
    
    ## SET UP WEBDRIVER

    # Set up the Selenium webdriver for Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.page_load_strategy = 'eager'

    driver = webdriver.Chrome(options=options)


    ## SET UP AND/OR LOAD EXISTING FILES

    # If this is a test run, only run this scrape for the first films.
    # Also, create a prefix of 'test_' for the names of any saved files.
    filename_prefix_test = ''
    if test_n_films:
        if len(target_film_df) >= test_n_films:
            target_film_df = target_film_df[:test_n_films]

        filename_prefix_test = 'test_'
    output_filename = filename_prefix_test + output_filename
    
    # Set the complete filepaths for the outputs.
    search_results_df_filepath_partial = f'{output_parentdir}/{output_filename}_mc_searchresults'
    info_df_filepath_partial = f'{output_parentdir}/{output_filename}_mc_info'
    review_df_filepath_partial = f'{output_parentdir}/{output_filename}_mc_reviews'

    # For these outputs, initialize empty dataframes to start. But if the
    # preceding filenames are present and this method is set to "add to 
    # existing," then load them from file.
    search_result_df = pd.DataFrame()
    info_df = pd.DataFrame()
    review_df = pd.DataFrame()

    master_searchresults_filepath = f'data/pkl/metacritic/master_files/master_mc_searchresults.pkl'
    master_info_filepath = f'data/pkl/metacritic/master_files/master_mc_info.pkl'
    master_reviews_filepath = f'data/pkl/metacritic/master_files/master_mc_reviews.pkl'

    if consult_master_files:
        if os.path.exists(master_searchresults_filepath):
            master_searchresults_df = pd.read_pickle(master_searchresults_filepath)

        if os.path.exists(master_info_filepath):
            master_info_df = pd.read_pickle(master_info_filepath)

        if os.path.exists(master_reviews_filepath):
            master_reviews_df = pd.read_pickle(master_reviews_filepath)

    else:
        if adding_to_existing_df:
            if os.path.exists(f'data/pkl/{search_results_df_filepath_partial}.pkl'):
                search_result_df = pd.read_pickle(f'data/pkl/{search_results_df_filepath_partial}.pkl')

            if os.path.exists(f'data/pkl/{info_df_filepath_partial}.pkl'):
                info_df = pd.read_pickle(f'data/pkl/{info_df_filepath_partial}.pkl')

            if os.path.exists(f'data/pkl/{review_df_filepath_partial}.pkl'):
                review_df = pd.read_pickle(f'data/pkl/{review_df_filepath_partial}.pkl')

    
    # Identify the film year attribute from the given dataset. It's
    # either 'Release Year' or 'Year'. (Inconsistently named across
    # scrapers, at the moment.)
    year_attr = None
    if 'Year' in target_film_df.columns:
        year_attr = 'Year'
    elif 'Release Year' in target_film_df.columns:
        year_attr = 'Release Year'


    # Initialize lists that will eventually form the desired outputs. These
    # will hold respective dictionaries of the films' search results, 
    # details, and critical reviews.
    search_results_dict_list = []
    info_dict_list = []
    review_dict_list = []

    # Start timing the imminent scraping.
    scrape_start = time.time()

    # For each film record, search that film on Metacritic and record 
    # the link of the best-matching result. The match is based on the
    # similarities of the titles and release years.
    for _, film_record in target_film_df.iterrows():

        # Assign the film's title, release year, and their concatenation to
        # dedicated variables.
        film_title = film_record['Title']
        film_year = film_record[year_attr]


        # Announce the film currently scraped for.
        print(f'\nCurrent scrape:\t{film_title} ({film_year})')

        if pd.isna(film_year):
            print(f'ABORTING SCRAPE: Required field \'Year\' was empty for film {film_title}.')
            continue

        # Check for bogus year entry, which Siskel submissions sometimes have.
        # example_str = '2017-2024'. A single, specific year is instead
        # required by my 'get_films_mc_link()' method, currently.
        year_range_pattern = r"\d{4}–\d{4}"
        if re.search(year_range_pattern, film_year):
            print("INVALID YEAR RECEIVED - Skipping this scrape for",
                  f'Title: {film_title}\nYear: {film_year}')
            continue

        # Retrieve the film's director, if offered in the received
        # dataframe of targeted films.
        if 'Director' in target_film_df.columns:
            film_director = film_record['Director']
            if pd.isna(film_director):
                film_director = None
        else:
            film_director = None

        # Check to see if the film's details and reviews have already been
        # scraped. If so for both, skip this film.

        # Checking the master file for a previous scrape of this film.
        already_searched, already_scraped_info, already_scraped_reviews = None, None, None
        if consult_master_files:
            if film_director:
                already_searched = not master_searchresults_df.loc[(master_searchresults_df['Title Searched'] == film_title) & (master_searchresults_df['Year Searched'] == film_year) & (master_searchresults_df['Director Searched'] ==  film_director)].empty
                already_scraped_info = not master_info_df.loc[(master_info_df['Title Searched'] == film_title) & (master_info_df['Year Searched'] == film_year) & (master_info_df['Director Searched'] ==  film_director)].empty
                already_scraped_reviews = not master_reviews_df.loc[(master_reviews_df['Title Searched'] == film_title) & (master_reviews_df['Year Searched'] == film_year) & (master_reviews_df['Director Searched'] ==  film_director)].empty
            else:
                already_searched = not master_searchresults_df.loc[(master_searchresults_df['Title Searched'] == film_title) & (master_searchresults_df['Year Searched'] == film_year)].empty
                already_scraped_info = not master_info_df.loc[(master_info_df['Title Searched'] == film_title) & (master_info_df['Year Searched'] == film_year)].empty
                already_scraped_reviews = not master_reviews_df.loc[(master_reviews_df['Title Searched'] == film_title) & (master_reviews_df['Year Searched'] == film_year)].empty
        

        # Checking existing file for a previous scrape.
        already_searched = None
        already_scraped_info, already_scraped_reviews = None, None
        if adding_to_existing_df:
            if os.path.exists(f'data/pkl/{search_results_df_filepath_partial}.pkl'):
                already_searched = not search_result_df.loc[(search_result_df['Title Searched'] == film_title) & (search_result_df['Year Searched'] == film_year) & (search_result_df['Director Searched'] ==  film_director)].empty
            if os.path.exists(f'data/pkl/{info_df_filepath_partial}.pkl'):
                already_scraped_info = not info_df.loc[(info_df['Title Searched'] == film_title) & (info_df['Year Searched'] == film_year) & (info_df['Director Searched'] ==  film_director)].empty
            if os.path.exists(f'data/pkl/{review_df_filepath_partial}.pkl'):
                already_scraped_reviews = not review_df.loc[(review_df['Title Searched'] == film_title) & (review_df['Year Searched'] == film_year) & (review_df['Director Searched'] ==  film_director)].empty
            
            # Skip the scrape if the film's details and critical reviews appear to
            # already have been scraped.
            if already_scraped_info and already_scraped_reviews:
                print(f"This film's production details and reviews have",
                      "already been scraped.\nSkipping...")
                continue
            elif already_searched and not already_scraped_info:
                # If a film has been searched before without finding a dedicated
                # Metacritic page, then it is skipped from being searched here
                # again.
                # (Many Siskel Center screenings can't be found on Metacritic,
                # and would cause many redundant searches without skipping
                # these cases.)
                print(f'This film has already been searched for, and in vain-',
                      'no corresponding page on Metacritic was found.',
                      '\nSkipping...')
                continue

        

        # SEARCH FOR FILM'S METACRITIC LINK

        chosen_link = mc_get_films_link(film_title,
                                        film_year,
                                        film_director,
                                        search_results_dict_list,
                                        driver)
        
        # SCRAPE FOR INFO AND REVIEWS AS NEEDED, if the search successfully
        # returns a link.

        if chosen_link:

            if not already_scraped_info:
                mc_info_scrape(film_title,
                               film_year,
                               chosen_link,
                               info_dict_list,
                               driver,
                               director_searched=film_director,
                               )
            else:
                print(f"Skipping detail scrape for {film_title} ({film_year})")
            
            if not already_scraped_reviews:
                mc_review_scrape(film_title,
                                    film_year,
                                    chosen_link,
                                    review_dict_list,
                                    driver,
                                    director_searched=film_director,
                                    )
            else:
                print(f"Skipping review scrape for {film_title} ({film_year})")
    
    
    ## SAVE DATA TO FILE

    various_output_necessities = [
        [review_dict_list, review_df, review_df_filepath_partial],
        [info_dict_list, info_df, info_df_filepath_partial],
        [search_results_dict_list, search_result_df, search_results_df_filepath_partial]
    ]
    
    for new_records, existing_data, output_filepath in various_output_necessities:
        combine_and_save_data(new_records, existing_data, output_filepath)


    # NOTE SCRAPE'S RUNTIME.
    scrape_runtime = time.time() - scrape_start
    scrape_runtime = round(scrape_runtime)
    runtime_min = scrape_runtime // 60
    runtime_sec = scrape_runtime % 60
    scrape_runtime_str = f'{runtime_min} m {runtime_sec} s'
    print(f'\nRuntime of this scrape: {scrape_runtime_str}')

    
    ## CLOSE THE WEBDRIVER
    driver.quit()


if __name__ == '__main__':

    # # For testing, read in my scraped Letterboxd Diary. Currently lacks directors!
    # target_films_df = pd.read_csv(f'data/csv/letterboxd/lb_diary_yoyoyodaboy.csv')
    # target_films_df['Release Year'] = target_films_df['Release Year'].astype(str) 
    
    # ALTERNATE FILE: Read in dataset with titles, release years, and directors.
    target_films_df = pd.read_pickle(f'data\pkl\siskel\siskel_inferior_show_info.pkl')


    # Call method to search for and scrape the films' Metacritic pages.
    prod_detail_df = mc_search_and_scrape(target_films_df, 
                                          test_n_films=5, 
                                          output_filename='siskel_inferior_show_info',
                                          output_parentdir='siskel',
                                        #   adding_to_existing_df=False,
                                          )
    # prod_detail_df = complete_mc_scrape(target_films_df, test_n_films=10, cr_filename='comp_mc_reviews', info_filename='comp_mc_info', searchresults_filename='comp_mc_searchresults', adding_to_existing_df=False)

    # (For the dev's reference: print this final dataframe.)
    print(prod_detail_df)
