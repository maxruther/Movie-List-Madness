import time

from selenium import webdriver

import re

import pandas as pd
import numpy as np

import os
from os.path import basename, splitext, dirname, exists

from mc_utilities.mc_info_scrape import mc_info_scrape
from mc_utilities.mc_review_scrape import mc_review_scrape
from mc_utilities.mc_get_films_link import mc_get_films_link


def combine_and_save_data(new_data: list[dict[str: str]],
                            existing_df: pd.DataFrame,
                            output_filepath: str,
                            ) -> None:

    new_data_df = pd.DataFrame(new_data)

    # Create dataframe of new records minus those preexisting.
    new_data_minus_existing_df = pd.concat([new_data_df, existing_df, existing_df]).drop_duplicates(keep=False)
    existing_df = pd.concat([existing_df, new_data_minus_existing_df], ignore_index=True)

    # Save the final dataframe of critic reviews to a csv file.
    existing_df.to_csv(f'{output_filepath.replace('/pkl/', '/csv/')}.csv', index=False)
    existing_df.to_pickle(f'{output_filepath}.pkl')


def mc_search_and_scrape(
        input_filepath: str = None,
        target_film_df: pd.DataFrame = None,
        test_n_films: int = 0,
        input_filename: str = 'search_n_scrape',
        adding_to_existing_df: bool = True,
        consult_master_files: bool = True,
        ) -> pd.DataFrame:
    
    ## SET UP WEBDRIVER

    # Set up the Selenium webdriver for Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.page_load_strategy = 'eager'

    driver = webdriver.Chrome(options=options)


    ## SET UP AND/OR LOAD EXISTING FILES

    if not input_filepath and not target_film_df:
        raise ValueError("Must provide, for the target films, either a"
        " dataframe or a filepath to a pickled one.")

    if input_filepath:
        input_filepath_minus_ext = splitext(input_filepath)[0]
        input_filename, input_extension = splitext(basename(input_filepath))
        input_dirname = dirname(input_filepath)

        if input_extension != '.pkl':
            raise ValueError("Input file must be a .pkl file.")

        if input_dirname[:9] != 'data/pkl/':
            raise ValueError("Input file must be in 'data/pkl/' or a subdirectory thereof.")
        
        if not os.path.exists(input_filepath):
            raise FileNotFoundError(f"Input file {input_filepath} does not exist.")
        else:
            target_film_df = pd.read_pickle(input_filepath)
        


    # If this is a test run, only run this scrape for the first films.
    # Also, create a prefix of 'test_' for the names of any saved files.
    if test_n_films:
        if len(target_film_df) >= test_n_films:
            target_film_df = target_film_df[:test_n_films]

        input_filepath_minus_ext = input_dirname + '/test_' + input_filename

    
    # Set the complete filepaths for the outputs.
    search_results_df_filepath_partial = f'{input_filepath_minus_ext}_mc_searchresults'
    info_df_filepath_partial = f'{input_filepath_minus_ext}_mc_info'
    review_df_filepath_partial = f'{input_filepath_minus_ext}_mc_reviews'

    prev_searchresults_df_exists = exists(f'{search_results_df_filepath_partial}.pkl')
    prev_info_df_exists = exists(f'{info_df_filepath_partial}.pkl')
    prev_review_df_exists = exists(f'{review_df_filepath_partial}.pkl')

    # For these outputs, initialize empty dataframes to start. But if the
    # preceding filenames are present and this method is set to "add to 
    # existing," then load them from file.
    search_result_df = pd.DataFrame()
    info_df = pd.DataFrame()
    review_df = pd.DataFrame()

    if adding_to_existing_df:
        if prev_searchresults_df_exists:
            search_result_df = pd.read_pickle(f'{search_results_df_filepath_partial}.pkl')

        if prev_info_df_exists:
            info_df = pd.read_pickle(f'{info_df_filepath_partial}.pkl')

        if prev_review_df_exists:
            review_df = pd.read_pickle(f'{review_df_filepath_partial}.pkl')
    

    # Master file setup
    master_searchresults_filepath_partial = 'data/pkl/metacritic/master_files/master_mc_searchresults'
    master_info_filepath_partial = 'data/pkl/metacritic/master_files/master_mc_info'
    master_reviews_filepath_partial = 'data/pkl/metacritic/master_files/master_mc_reviews'

    master_searchresults_df_exists = exists(f'{master_searchresults_filepath_partial}.pkl')
    master_info_df_exists = exists(f'{master_info_filepath_partial}.pkl')
    master_reviews_df_exists = exists(f'{master_reviews_filepath_partial}.pkl')

    master_searchresults_df = pd.DataFrame()
    master_info_df = pd.DataFrame() 
    master_reviews_df = pd.DataFrame()

    if consult_master_files:
        if master_searchresults_df_exists:
            master_searchresults_df = pd.read_pickle(f'{master_searchresults_filepath_partial}.pkl')

        if master_info_df_exists:
            master_info_df = pd.read_pickle(f'{master_info_filepath_partial}.pkl')

        if master_reviews_df_exists:
            master_reviews_df = pd.read_pickle(f'{master_reviews_filepath_partial}.pkl')


    

    
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
    searchresults_dict_list = []
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


        # Retrieve the film's director, if offered in the received
        # dataframe of targeted films.
        director_attr_exists = 'Director' in target_film_df.columns
        if director_attr_exists:
            film_director = film_record['Director']
            # if pd.isna(film_director):
            #     film_director = None
        else:
            film_director = None
        

        # Announce the film currently scraped for.
        # scrape_announce_str = f'\nCurrent scrape:\t{film_title} ({film_year})'
        scrape_announce_str = f'\nCurrent scrape:\t{film_title}'
        if film_year and not pd.isna(film_year):
            scrape_announce_str += f' ({film_year})'
        if film_director and not pd.isna(film_director):
            scrape_announce_str += f' by {film_director}'
        print(scrape_announce_str)
        
        if pd.isna(film_year):
            print(f'ABORTING SCRAPE: Required field \'Year\' was empty for this film.')
            continue
        
        # Check for bogus year entry, which Siskel submissions sometimes have.
        # example_str = '2017-2024'. A single, specific year is instead
        # required by my 'get_films_mc_link()' method, currently.
        year_range_pattern = r"\d{4}–\d{4}"
        if re.search(year_range_pattern, film_year):
            print("INVALID YEAR RECEIVED - Skipping this scrape for",
                  f'Title: {film_title}\nYear: {film_year}')
            continue
        
        # Check to see if the film's details and reviews have already been
        # scraped. If so for both, skip this film.

        def filmsearch_mask(df: pd.DataFrame, title: str, year: str, director: str) -> pd.Series:
            if director_attr_exists:
                return (df['Title Searched'] == title) & (df['Year Searched'] == year) & ((df['Director Searched'] ==  director) | (df['Director Searched'].isna() & pd.isna(director)))
            else:
                return (df['Title Searched'] == title) & (df['Year Searched'] == year)

        def check_df_for_search_keys(df: pd.DataFrame, title: str, year: str, director: str) -> bool:
            if director_attr_exists:
                return not df.loc[(df['Title Searched'] == title) & (df['Year Searched'] == year) & ((df['Director Searched'] ==  director) | (df['Director Searched'].isna() & pd.isna(director)))].empty
            else:
                return not df.loc[(df['Title Searched'] == title) & (df['Year Searched'] == year)].empty

        # Checking the master file for a previous scrape of this film.
        already_searched_master, already_scraped_info_master, already_scraped_reviews_master = None, None, None
        if consult_master_files:
            if master_searchresults_df_exists:
                already_searched_master = check_df_for_search_keys(master_searchresults_df, film_title, film_year, film_director)
            if master_info_df_exists:
                already_scraped_info_master = check_df_for_search_keys(master_info_df, film_title, film_year, film_director)
            if master_reviews_df_exists:
                already_scraped_reviews_master = check_df_for_search_keys(master_reviews_df, film_title, film_year, film_director)
        
        # Checking existing file for a previous scrape.
        already_searched = None
        already_scraped_info, already_scraped_reviews = None, None
        if adding_to_existing_df:
            if prev_searchresults_df_exists:
                already_searched = check_df_for_search_keys(search_result_df, film_title, film_year, film_director)
            if prev_info_df_exists:
                already_scraped_info = check_df_for_search_keys(info_df, film_title, film_year, film_director)
            if prev_review_df_exists:
                already_scraped_reviews = check_df_for_search_keys(review_df, film_title, film_year, film_director)

            
        # If the master files are being consulted, and the film's key
        # fields are there contained, then skip the scrape and instead
        # pull records from those files.
        if consult_master_files:
            if already_searched_master and already_scraped_info_master and already_scraped_reviews_master:
                print(f"The master files suggest that this film's production details and reviews have",
                      "already been scraped.\nSkipping scrape and pulling from there..."
                      )
                
                master_searchres_recs_as_dicts = master_searchresults_df.loc[filmsearch_mask(master_searchresults_df, film_title, film_year, film_director)].to_dict(orient='records')
                for dict in master_searchres_recs_as_dicts:
                    searchresults_dict_list.append(dict)
                print("Pulled search results from master file.")

                master_info_recs_as_dicts = master_info_df.loc[filmsearch_mask(master_info_df, film_title, film_year, film_director)].to_dict(orient='records')
                for dict in master_info_recs_as_dicts:
                    info_dict_list.append(dict)
                print("Pulled info from master file.")

                master_review_recs_as_dicts = master_reviews_df.loc[filmsearch_mask(master_reviews_df, film_title, film_year, film_director)].to_dict(orient='records')
                for dict in master_review_recs_as_dicts:
                    review_dict_list.append(dict)
                print("Pulled reviews from master file.")

                continue

            elif already_searched_master and not already_scraped_info_master:
                # If a film has been searched before without finding a dedicated
                # Metacritic page, then it is skipped from being searched here
                # again.
                # (Many Siskel Center screenings can't be found on Metacritic,
                # and would cause many redundant searches without skipping
                # these cases.)
                print(f'The master file suggests that this film has already been searched for, and in vain-',
                        'no corresponding page on Metacritic was found.',
                        '\nSkipping...')
                

                # Pull the records from the master files instead of scraping.
                # I query the master file dfs' relevant rows, convert them
                # to dictionaries, and then append them to this method's 
                # accumulating dictionary lists.
                master_searchres_recs_as_dicts = master_searchresults_df.loc[filmsearch_mask(master_searchresults_df, film_title, film_year, film_director)].to_dict(orient='records')
                for dict in master_searchres_recs_as_dicts:
                    searchresults_dict_list.append(dict)

                continue
            

        # Skip the scrape if the film's details and critical reviews appear to
        # already have been scraped.
        if already_searched and already_scraped_info and already_scraped_reviews:
            
            prev_searchres_recs_as_dicts = search_result_df.loc[filmsearch_mask(search_result_df, film_title, film_year, film_director)].to_dict(orient='records')
            for dict in prev_searchres_recs_as_dicts:
                searchresults_dict_list.append(dict)
            print("Pulled search results from preexisting file.")

            prev_info_recs_as_dicts = info_df.loc[filmsearch_mask(info_df, film_title, film_year, film_director)].to_dict(orient='records')
            for dict in prev_info_recs_as_dicts:
                info_dict_list.append(dict)
            print("Pulled info from preexisting file.")

            prev_review_recs_as_dicts = review_df.loc[filmsearch_mask(review_df, film_title, film_year, film_director)].to_dict(orient='records')
            for dict in prev_review_recs_as_dicts:
                review_dict_list.append(dict)
            print("Pulled reviews from preexisting file.")

            continue

        elif already_searched and not already_scraped_info:
            print(f'The preexisting file suggests that this film has already been searched for, and in vain-',
                        'no corresponding page on Metacritic was found.',
                        '\nSkipping...')
                

            # Pull the records from the master files instead of scraping.
            # I query the master file dfs' relevant rows, convert them
            # to dictionaries, and then append them to this method's 
            # accumulating dictionary lists.
            prev_searchres_recs_as_dicts = search_result_df.loc[filmsearch_mask(search_result_df, film_title, film_year, film_director)].to_dict(orient='records')
            for dict in prev_searchres_recs_as_dicts:
                searchresults_dict_list.append(dict)
            print("Pulled search results from preexisting file.")

            continue
    

        # SEARCH FOR FILM'S METACRITIC LINK

        chosen_link = mc_get_films_link(film_title,
                                        film_year,
                                        film_director,
                                        searchresults_dict_list,
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
        [searchresults_dict_list, search_result_df, search_results_df_filepath_partial]
    ]

    
    if consult_master_files:
        masterfile_output_necessities = [
        [review_dict_list, master_reviews_df, master_reviews_filepath_partial],
        [info_dict_list, master_info_df, master_info_filepath_partial],
        [searchresults_dict_list, master_searchresults_df, master_searchresults_filepath_partial]
        ]

        for arg_list in masterfile_output_necessities:
            various_output_necessities.append(arg_list)

    
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
    
    
    mc_search_and_scrape(
        # input_filepath='data/pkl/ebert/ebert_recent_reviews.pkl',
        input_filepath='data/pkl/siskel/siskel_inferior_show_info.pkl',
        # input_filepath='data/pkl/musicbox/musicbox_show_info.pkl',
        # input_filepath='data/pkl/my_watched_films/my_watched_films.pkl',

        # test_n_films=5,
        # adding_to_existing_df=False,
        # consult_master_files=False,
        )
