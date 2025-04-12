from selenium import webdriver

import pandas as pd
from os import makedirs
from os.path import dirname, exists
import time

def create_chromedriver(page_load_strategy='eager'):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.page_load_strategy = page_load_strategy

    driver = webdriver.Chrome(options=options)
    return driver


def add_new_data_to_existing(
        new_data_df: pd.DataFrame,
        existing_data_df: pd.DataFrame,
        ) -> pd.DataFrame:
    
    # Create dataframe of new records minus those preexisting.
    new_data_minus_existing_df = pd.concat([new_data_df, existing_data_df, existing_data_df]).drop_duplicates(keep=False)
    result_df = pd.concat([existing_data_df, new_data_minus_existing_df], ignore_index=True)

    return result_df


def save_output_df_to_dirs(df: pd.DataFrame,
                           testing: int | bool,
                           output_filename: str,
                           output_subdir,
                           ) -> None:

    # Set the filepath of the directories that
    # will house the scraped data.
    output_dir_pkl = f'data/pkl/{output_subdir}'
    output_dir_csv = f'data/csv/{output_subdir}'

    # If testing, output to a subdir named 'test'.
    if testing:
        output_dir_pkl += '/test'
        output_dir_csv += '/test'

    # Create the output directories, if they don't already exist.
    makedirs(output_dir_pkl, exist_ok=True)
    makedirs(output_dir_csv, exist_ok=True)
    
    # If testing, prepend the output filenames with 'test_'.
    testing_prefix = 'test_' if testing else ''

    # Save to file the dataframe of the scraped Letterboxd diary.
    df.to_pickle(f'{output_dir_pkl}/{testing_prefix}{output_filename}.pkl')
    df.to_csv(f'{output_dir_csv}/{testing_prefix}{output_filename}.csv', index=False)


def get_existing_df_if_exists(
        output_filename: str,
        output_subdir: str,
        testing: int | bool,
        ):
    # Load the relevant data-scrape file if it exists (in pkl format).
    # Otherwise, instantiate an empty dataframe in its place.
    if testing:
        output_filepath = f'data/pkl/{output_subdir}/test/test_{output_filename}.pkl'
    else:
        output_filepath = f'data/pkl/{output_subdir}/{output_filename}.pkl'
    existing_data_filepath = output_filepath

    existing_df = pd.DataFrame()
    if exists(existing_data_filepath):
        existing_df = pd.read_pickle(existing_data_filepath)
    
    return existing_df


def print_runtime_of_scrape(
    scrape_start: int,
) -> int:
    """Calculate and print the runtime of the scrape in minutes and
    seconds, given the time of scrape's start (in seconds)."""

    scrape_runtime = time.time() - scrape_start
    scrape_runtime = round(scrape_runtime)

    runtime_min = scrape_runtime // 60
    runtime_sec = scrape_runtime % 60
    scrape_runtime_str = f'{runtime_min} m {runtime_sec} s'
    print(f'\nRuntime of this scrape: {scrape_runtime_str}')

    return scrape_runtime