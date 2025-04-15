import time
import re
import pandas as pd
from os.path import basename, splitext, dirname, makedirs, exists

from utils import create_chromedriver, get_existing_df_if_exists
from utils import add_new_data_to_existing, save_output_df_to_dirs
from utils import print_runtime_of_scrape

if __name__ == '__main__':
    from mc_utilities.mc_info_scrape import mc_info_scrape
    from mc_utilities.mc_review_scrape import mc_review_scrape
    from mc_utilities.mc_get_films_link import mc_get_films_link
else:
    try:
        print(__name__)
        from critic_ratings.scrapers.mc_utilities.mc_info_scrape import mc_info_scrape
        from critic_ratings.scrapers.mc_utilities.mc_review_scrape import mc_review_scrape
        from critic_ratings.scrapers.mc_utilities.mc_get_films_link import mc_get_films_link
    except:
        raise Exception(f"ERROR - {basename(__file__)}: Failed to import methods 'mc_info_scrape', 'mc_review_scrape', and 'mc_get_films_link'.")


def mc_search_and_scrape(
        input_filepath: str = None,
        target_film_df: pd.DataFrame = None,
        test_n_films: int = 0,
        input_filename: str = 'search_n_scrape',
        adding_to_existing_df: bool = True,
        consult_master_files: bool = True,
        ) -> pd.DataFrame:
    
    ## SET UP WEBDRIVER
    driver = create_chromedriver()

    ## VALIDATE INPUT FILEPATH AND LOAD THE FILMS SUBJECT TO THIS SCRAPING.

    if not input_filepath and not target_film_df:
        raise ValueError("Must provide, for the target films, either a"
        " dataframe or a filepath to a pickled one.")

    if input_filepath:
        input_filename, input_extension = splitext(basename(input_filepath))
        input_dirname = dirname(input_filepath)
        input_subdir = input_dirname[9:]

        if input_extension != '.pkl':
            raise ValueError("Input file must be a .pkl file.")

        if input_dirname[:9] != 'data/pkl/' and input_dirname[:9] != 'data\\pkl\\':
            raise ValueError("Input file must be in 'data/pkl/' or a subdirectory thereof.")
        
        if not exists(input_filepath):
            raise FileNotFoundError(f"Input file {input_filepath} does not exist.")
        else:
            target_film_df = pd.read_pickle(input_filepath)
        

    # # OUTPUT FILENAME SETUP

    # Set the names of the different Metacritic scrape output files
    searchres_filename_suffix = '_mc_searchresults'
    info_filename_suffix = '_mc_info'
    review_filename_suffix = '_mc_reviews'

    searchres_filename = input_filename + searchres_filename_suffix
    info_filename = input_filename + info_filename_suffix
    review_filename = input_filename + review_filename_suffix

    mc_scrape_subdir = input_subdir + '/mc_scrape'


    # # LOAD EXISTING MC-SCRAPED DATA (IF PRESENT)

    # Initialize a dictionary of temporary dataframes, to hold each
    # scrape type's data as we iteratively attempt to load it from file.
    existing_dfs = {
        searchres_filename: pd.DataFrame(),
        info_filename: pd.DataFrame(),
        review_filename: pd.DataFrame(),
    }

    # Iterate through the scrape types that form the dictionary's keys,
    # using that scrape-type's filename to load its corresponding,
    # preexisting data (if indeed preexisting. Otherwise, gets a blank
    # df.)
    existing_sr_df, existing_info_df, existing_review_df = [pd.DataFrame()] * 3
    if adding_to_existing_df:
        for scrape_filename in existing_dfs:
            existing_dfs[scrape_filename] = get_existing_df_if_exists(
                scrape_filename,
                mc_scrape_subdir,
                test_n_films,
            )

        # Assign the loaded df's of existing data (or blank df's) to
        # the variables that will be referred to henceforth. (The
        # dictionary 'master_dfs' was only created for the purpose of
        # the iterative reassignment above.)
        existing_sr_df = existing_dfs[searchres_filename]
        existing_info_df = existing_dfs[info_filename]
        existing_review_df = existing_dfs[review_filename]

    
    # # MASTERFILE SETUP

    # Set the masterfiles' names and subdirectory of 'data/pkl/'.
    master_filename = 'master'
    master_subdir = 'metacritic/master_files'

    master_sr_filename = master_filename + searchres_filename_suffix
    master_info_filename = master_filename + info_filename_suffix
    master_review_filename = master_filename + review_filename_suffix

    master_dfs = {
        master_sr_filename: pd.DataFrame(),
        master_info_filename: pd.DataFrame(),
        master_review_filename: pd.DataFrame(),
    }

    master_sr_df, master_info_df, master_review_df = [pd.DataFrame()] * 3
    if consult_master_files:
        for scrape_filename in master_dfs:
            master_dfs[scrape_filename] = get_existing_df_if_exists(
                scrape_filename,
                master_subdir,
                test_n_films,
                )
        
        master_sr_df = master_dfs[master_sr_filename]
        master_info_df = master_dfs[master_info_filename]
        master_review_df = master_dfs[master_review_filename]

    
    # # MISC PREPARATION FOR SCRAPE

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

    # If this is a test run, only run this scrape for the first films.
    if test_n_films:
        if len(target_film_df) >= test_n_films:
            target_film_df = target_film_df[:test_n_films]

    
    # # SCRAPE THE METACRITIC PAGES

    # For each film record given, search that film on Metacritic and record 
    # the link of the best-matching result. The match is based on the
    # similarities of the titles, release years, and directors.
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
        year_range_pattern = r"\d{4}(?:–|, |-)\d{4}"
        if re.search(year_range_pattern, film_year):
            print("INVALID YEAR RECEIVED - Skipping this scrape for",
                  f'Title: {film_title}\nYear: {film_year}')
            continue


        # # CHECK WHETHER SCRAPE WAS ALREADY DONE PREVIOUSLY
        
        # Check to see if the film's details and reviews have already been
        # scraped. If so for both, skip this film.

        # This method works as a pandas mask, to pull up records that 
        # fit the search condition.
        def filmsearch_mask(df: pd.DataFrame, title: str, year: str, director: str) -> pd.DataFrame:
            if director_attr_exists:
                return (df['Title Searched'] == title) & (df['Year Searched'] == year) & ((df['Director Searched'] ==  director) | (df['Director Searched'].isna() & pd.isna(director)))
            else:
                return (df['Title Searched'] == title) & (df['Year Searched'] == year)

        # This method
        def check_df_for_search_keys(df: pd.DataFrame, title: str, year: str, director: str) -> bool:
            if director_attr_exists:
                return not df.loc[(df['Title Searched'] == title) & (df['Year Searched'] == year) & ((df['Director Searched'] ==  director) | (df['Director Searched'].isna() & pd.isna(director)))].empty
            else:
                return not df.loc[(df['Title Searched'] == title) & (df['Year Searched'] == year)].empty

        # Checking the master file for a previous scrape of this film.
        already_searched_master, already_scraped_info_master, already_scraped_reviews_master = None, None, None
        if consult_master_files:
            if not master_sr_df.empty:
                already_searched_master = check_df_for_search_keys(master_sr_df, film_title, film_year, film_director)
            if not master_info_df.empty:
                already_scraped_info_master = check_df_for_search_keys(master_info_df, film_title, film_year, film_director)
            if not master_review_df.empty:
                already_scraped_reviews_master = check_df_for_search_keys(master_review_df, film_title, film_year, film_director)
        
        # Checking existing file for a previous scrape.
        already_searched, already_scraped_info, already_scraped_reviews = None, None, None
        if adding_to_existing_df:
            # if prev_searchresults_df_exists:
            if not existing_sr_df.empty:
                already_searched = check_df_for_search_keys(existing_sr_df, film_title, film_year, film_director)
            # if prev_info_df_exists:
            if not existing_info_df.empty:
                already_scraped_info = check_df_for_search_keys(existing_info_df, film_title, film_year, film_director)
            # if prev_review_df_exists:
            if not existing_review_df.empty:
                already_scraped_reviews = check_df_for_search_keys(existing_review_df, film_title, film_year, film_director)

            
        # If the master files are being consulted, and the film's key
        # fields are there contained, then skip the scrape and instead
        # pull records from those files.
        if consult_master_files:
            if already_searched_master and already_scraped_info_master and already_scraped_reviews_master:
                print(f"The master files suggest that this film's production details and reviews have",
                      "already been scraped.\nSkipping scrape and pulling from there..."
                      )
                
                master_searchres_recs_as_dicts = master_sr_df.loc[filmsearch_mask(master_sr_df, film_title, film_year, film_director)].to_dict(orient='records')
                for dict in master_searchres_recs_as_dicts:
                    searchresults_dict_list.append(dict)
                print("Pulled search results from master file.")

                master_info_recs_as_dicts = master_info_df.loc[filmsearch_mask(master_info_df, film_title, film_year, film_director)].to_dict(orient='records')
                for dict in master_info_recs_as_dicts:
                    info_dict_list.append(dict)
                print("Pulled info from master file.")

                master_review_recs_as_dicts = master_review_df.loc[filmsearch_mask(master_review_df, film_title, film_year, film_director)].to_dict(orient='records')
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
                master_searchres_recs_as_dicts = master_sr_df.loc[filmsearch_mask(master_sr_df, film_title, film_year, film_director)].to_dict(orient='records')
                for dict in master_searchres_recs_as_dicts:
                    searchresults_dict_list.append(dict)

                continue
            

        # Skip the scrape if the film's details and critical reviews appear to
        # already have been scraped.
        if already_searched and already_scraped_info and already_scraped_reviews:
            
            prev_searchres_recs_as_dicts = existing_sr_df.loc[filmsearch_mask(existing_sr_df, film_title, film_year, film_director)].to_dict(orient='records')
            for dict in prev_searchres_recs_as_dicts:
                searchresults_dict_list.append(dict)
            print("Pulled search results from preexisting file.")

            prev_info_recs_as_dicts = existing_info_df.loc[filmsearch_mask(existing_info_df, film_title, film_year, film_director)].to_dict(orient='records')
            for dict in prev_info_recs_as_dicts:
                info_dict_list.append(dict)
            print("Pulled info from preexisting file.")

            prev_review_recs_as_dicts = existing_review_df.loc[filmsearch_mask(existing_review_df, film_title, film_year, film_director)].to_dict(orient='records')
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
            prev_searchres_recs_as_dicts = existing_sr_df.loc[filmsearch_mask(existing_sr_df, film_title, film_year, film_director)].to_dict(orient='records')
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
    
    # # SCRAPE CONCLUDED

    
    # # CREATE DATAFRAMES FROM DICTS AND SAVE TO FILE

    # From the dictionary-lists of new data, create dataframes.
    new_sr_data_df = pd.DataFrame(searchresults_dict_list)
    new_info_data_df = pd.DataFrame(info_dict_list)
    new_review_data_df = pd.DataFrame(review_dict_list)

    # For the various scrape outputs (search results, info, and reviews)
    # create lists of the variables that are necessary for that output's
    # finalization and filesaving.
    various_output_necessities = [
        [new_sr_data_df, existing_sr_df,
         searchres_filename, mc_scrape_subdir],

        [new_info_data_df, existing_info_df, 
         info_filename, mc_scrape_subdir],

        [new_review_data_df, existing_review_df, 
         review_filename, mc_scrape_subdir],
    ]
    
    # If the masterfiles were referenced, create sets of output
    # arguments for those too.
    if consult_master_files:
        masterfile_output_necessities = [
            [new_sr_data_df, master_sr_df,
             master_sr_filename, master_subdir],

            [new_info_data_df, master_info_df,
             master_info_filename, master_subdir],
              
            [new_review_data_df, master_review_df,
             master_review_filename, master_subdir],
            ]

        # Add these masterfile filsaving-argument-lists to the list
        # of those for the targetfilm-specific output.
        various_output_necessities += masterfile_output_necessities

    # Iterate through all output sets to combine the new data with that
    # existing and save it all to the appropriate subdirectories.
    for new_data_df, existing_data_df, output_filename, output_subdir in various_output_necessities:

        # Combine the new data with the existing, leaving out duplicates.
        final_data_df = add_new_data_to_existing(new_data_df, existing_data_df)

        # Save this combined, final data to pkl and csv files, in an
        # appropriate subdirectory.
        save_output_df_to_dirs(final_data_df, test_n_films, output_filename, output_subdir)


    # # PRINT SCRAPE'S RUNTIME.
    print_runtime_of_scrape(scrape_start)

    
    # # CLOSE THE WEBDRIVER
    driver.quit()


if __name__ == '__main__':
    
    
    mc_search_and_scrape(
        # input_filepath='data/pkl/ebert/ebert_recent_reviews.pkl',
        # input_filepath='data/pkl/ebert/test/test_ebert_recent_reviews.pkl',
        # input_filepath='data/pkl/siskel/siskel_show_info.pkl',
        # input_filepath='data/pkl/musicbox/musicbox_show_info.pkl',
        input_filepath='data/pkl/my_watched_films/my_watched_films.pkl',

        # test_n_films=3,
        # adding_to_existing_df=False,
        # consult_master_files=False,
        )
