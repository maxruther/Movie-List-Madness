import re
from selenium import webdriver
from selenium.webdriver.common.by import By

import pandas as pd
from os import makedirs
from os.path import dirname, exists
import time

def tech_summary_list_to_dict(tech_summary_list: list[str],
                                ) -> dict[str: int | str]:
    """For the Music Box scrape, this function takes a list of strings 
    containing a film's technical details and returns a dictionary 
    thereof. Such a dictionary is more suitable for the scheduling 
    methods that operate on this data."""

    tech_details = {}

    year_pattern = r'^(\d{4})$'
    runtime_pattern = r'^(\d*) mins?$'
    format_pattern = r'(^DCP$|^\d\.\dmm$|^\d{1,3}mm$)'

    for tech_detail in tech_summary_list:

        year_match = re.search(year_pattern, tech_detail)
        runtime_match = re.search(runtime_pattern, tech_detail)
        format_match = re.search(format_pattern, tech_detail)

        if year_match:
            tech_details['Year'] = year_match.group(1)
            # print(tech_details['Year'])
            # print(type(tech_details['Year']))
        elif runtime_match:
            tech_details['Runtime'] = int(runtime_match.group(1))
            # print(tech_details['Runtime'])
            # print(type(tech_details['Runtime']))
        elif format_match:
            tech_details['Format'] = format_match.group(1)
            # print(tech_details['Format'])
            # print(type(tech_details['Format']))

    return tech_details


def parse_show_name(show_name: str,
                        ) -> str:
        """Parse a Siskel show's title into those of the series and film,
        which sometimes comprise it.
        
        An auxiliary method of the siskel_scrape."""

        film_title = None
        series_prepends = None


        if ': ' in show_name:
            parsed_show_name = show_name.split(': ')

            # In the event that the film title contains a single
            # colon, detect and combine its erroneously split 
            # segments.
            if len(parsed_show_name) >= 2:
                potential_title_segment = parsed_show_name[-2]

                some_valid_series_names = ['OFF CENTER', 
                                        'ARTHUR ERICKSON',
                                        'ADFF',
                                        ]

                if potential_title_segment not in some_valid_series_names and \
                not any(char.islower() for char in potential_title_segment):
                    film_title = ': '.join(parsed_show_name[-2:])
                    series_prepends = parsed_show_name[:-2]
                else:
                    film_title = parsed_show_name[-1]
                    series_prepends = parsed_show_name[:-1]
        else:
            film_title = show_name
            series_prepends = None

        return film_title, series_prepends


def create_chromedriver(
          page_load_strategy: str = 'eager',
          ) -> webdriver.Chrome:
     options = webdriver.ChromeOptions()
     options.add_argument('--ignore-certificate-errors')
     options.add_argument('--ignore-ssl-errors')
     options.page_load_strategy = page_load_strategy
     
     driver = webdriver.Chrome(options=options)
     return driver


def print_runtime_of_scrape(
          scrape_start: int,
          ) -> None:
        """Calculate and print the runtime of the scrape in minutes and
        seconds, given the time of scrape's start (in seconds)."""

        scrape_runtime = time.time() - scrape_start
        scrape_runtime = round(scrape_runtime)

        runtime_min = scrape_runtime // 60
        runtime_sec = scrape_runtime % 60
        scrape_runtime_str = f'{runtime_min} m {runtime_sec} s'
        print(f'\n\nRuntime of this scrape: {scrape_runtime_str}\n')

        return scrape_runtime


def save_output_df_to_dirs(df: pd.DataFrame,
                           testing: int | bool,
                           output_filename: str,
                           output_subdir: str,
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


def add_new_data_to_existing(
        new_data_df: pd.DataFrame,
        existing_data_df: pd.DataFrame,
        ) -> pd.DataFrame:
    
    # Create dataframe of new records minus those preexisting.
    new_data_minus_existing_df = pd.concat([new_data_df, existing_data_df, existing_data_df]).drop_duplicates(keep=False)
    result_df = pd.concat([existing_data_df, new_data_minus_existing_df], ignore_index=True)

    return result_df


def save_driver_html_to_file(
        driver: webdriver.Chrome,
        output_subdir: str,
        output_filename: str = 'sourceHTML',
        ) -> None:
    
    # Get the HTML source of the current page.
    html_source = driver.page_source

    if output_filename == 'sourceHTML':
        if 'musicbox' in output_subdir:
            # Name output file with page's main header (ex. 'April 2025')
            output_filename = driver.find_element(By.CSS_SELECTOR, 'h1.page-title').text.strip()
            output_filename = output_filename.replace(' ', '')
        elif 'siskel' in output_subdir:
            output_filename = driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/div/div/section/div/div/div[2]/div/div/table/caption').text.strip()
            output_filename = output_filename.replace(' ', '')
    
    # Set the filepath of the directories that
    # will house this html that will be scraped imminently.
    output_dir_html = f'data/html/{output_subdir}'

    # Set the date stamp for the output filename.
    date_stamp = time.strftime('%Y-%m-%d')

    # Create the output directory, if it doesn't already exist.
    makedirs(output_dir_html, exist_ok=True)

    # Save the HTML of the current page to a file.
    with open(f'{output_dir_html}/{output_filename}__{date_stamp}.html',
              'w', encoding='utf-8') as file:
        file.write(html_source)


def move_scrape_cols_to_end(
        df,
        scrape_cols=['Theater', 'Scrape_Datetime'],
        ):
    other_cols = [col for col in df.columns if col not in scrape_cols]
    return df[other_cols + list(scrape_cols)]


def save_scrape_and_add_to_existing(
        new_data_df: pd.DataFrame,
        output_filename: str,
        output_subdir: str,
        testing: int | bool,
        ) -> None:
    
    single_scrape_subdir = output_subdir + '/single_scrapes'
    makedirs(single_scrape_subdir, exist_ok=True)
    
    # Save newly scraped data to file.
    date_stamp = time.strftime('%Y-%m-%d')
    save_output_df_to_dirs(new_data_df, testing, 
                           f"{output_filename}_{date_stamp}",
                           single_scrape_subdir)

    # Get the existing dataframe, if it exists.
    existing_df = get_existing_df_if_exists(output_filename, output_subdir, testing)

    # Add the new data to the existing data.
    updated_df = add_new_data_to_existing(new_data_df, existing_df)

    # Move the scrape meta attributes to the rightmost, for readability.
    updated_df = move_scrape_cols_to_end(updated_df)

    # Save the updated dataframe to file.
    save_output_df_to_dirs(updated_df, testing, 
                           output_filename,
                           output_subdir)


