import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import pickle
import csv

import pandas as pd

from bs4 import BeautifulSoup


def get_users_diary_links(user_url: str = 'yoyoyodaboy',
                          output_subdir: str = 'letterboxd',
                          test_n_films: int = 0,
                          ) -> list[str]:
    
    # Set up the Selenium Chromium driver
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    # options.page_load_strategy = 'eager'
    options.page_load_strategy = 'none'

    driver = webdriver.Chrome(options)
    driver.implicitly_wait(3)

    # Navigate to user's film diary page.
    driver.get(f"https://letterboxd.com/{user_url}/films/diary/")

    # From that page, retrieve the diary's page count.
    diary_pages_xpath = '//*[@id="content"]/div/section[2]/div[2]/div[3]/ul/li/a'
    diary_page_elems = driver.find_elements(By.XPATH, diary_pages_xpath)
    diary_page_count = diary_page_elems[-1].get_attribute('text')

    # Initialize lists where the films' titles, release years, and 
    # letterboxd links will be stored.
    all_film_links = []
    all_film_titles = []
    all_film_release_yrs = []

    diary_record_list = []

    # # Scrape each page of the film diary for that information.
    # (If testing, only process the first page of the diary.)
    if test_n_films:
        diary_page_count = 1
    for i in range(1, int(diary_page_count) + 1):
        # Navigate to the i-th diary page.
        diary_page_link = f'https://letterboxd.com/{user_url}/films/diary/page/{str(i)}/'
        driver.get(diary_page_link)

        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div#content-nav"))
            )
        finally:
            pass

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        diary_entry_elems = soup.select('tr.diary-entry-row')

        if test_n_films:
            diary_entry_elems = list(diary_entry_elems)[:test_n_films]
        for entry_elem in diary_entry_elems:

            film_title = None
            film_title_elem = entry_elem.select_one('td.td-film-details')
            if film_title_elem:
                film_title_header_elem = film_title_elem.select_one('h3')
                if film_title_header_elem:
                    film_title = film_title_header_elem.text.strip()
                    print(film_title)

            film_year = None
            film_year_elem = entry_elem.select_one('td.td-released')
            if film_year_elem:
                film_year = film_year_elem.text.strip()
                print(film_year)

            rating = None
            rating_elem = entry_elem.select_one('td.td-rating')
            # print(rating_elem)
            if rating_elem:
                star_rating = rating_elem.text.strip()
                # Initialize the numeric rating to the count of full stars.
                rating = star_rating.count('\u2605')
                # If there is a half-star, add 0.5 to that.
                if '\u00BD' in star_rating:
                    rating += 0.5
                print(rating)

            watch_date = None
            watch_date_elem = entry_elem.select_one('td.td-day.diary-day')
            if watch_date_elem:
                watch_date_link_elem = watch_date_elem.select_one('a')
                if watch_date_link_elem:
                    watch_date_link = watch_date_link_elem.get('href')
                    watch_date = '-'.join(watch_date_link.split('/')[-4:-1])
                    print(watch_date)
            
            lb_film_link = None
            film_details_elem = entry_elem.select_one('td.td-film-details')
            if film_details_elem:
                header_elem = film_details_elem.select_one('h3')
                if header_elem:
                    lb_watch_link_elem = header_elem.select_one('a')
                    if lb_watch_link_elem:
                        lb_watch_link = lb_watch_link_elem.get('href').strip()
                        lb_film_link_relative = lb_watch_link.replace(f'/{user_url}', '')
                        lb_film_link = 'https://letterboxd.com/' + lb_film_link_relative
                        print(lb_film_link)

                    # lb_film_link_relative = film_details_elem.get('data-film-link').strip()
                    # lb_film_link = 'https://letterboxd.com/' + lb_film_link_relative
                    # print(lb_film_link)

            director, us_release_date = None, None
            if lb_film_link:

                crew_link = lb_film_link + '/crew'

                driver.get(crew_link)
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.tabbed-content-block.column-block.-crewroles"))
                    )
                finally:
                    pass

                lb_crew_credits = {}

                crew_soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                crew_section_elem = crew_soup.select_one('div.tabbed-content-block.column-block.-crewroles')
                if crew_section_elem:
                    crew_role_elems = crew_section_elem.select('h3')
                    crew_name_elems = crew_section_elem.select('div.text-sluglist')
                    if crew_role_elems and crew_name_elems:
                        for role_elem, name_div_elem in zip(crew_role_elems, crew_name_elems):
                            # Initialize the crew role and credited name to 'None'.
                            role, names = None, None

                            # Get the crew role from the last role element, 
                            role = role_elem.text.strip().split('\n')[0]

                            # Get the credited names for this role.
                            name_p_elem = name_div_elem.select_one('p')
                            if name_p_elem:
                                name_list = []
                                for elem in name_p_elem:
                                    if elem.text.strip():
                                        name_list.append(elem.text.strip())
                                # print(name_list)
                                names = ', '.join(name_list)
                                # print(names)

                            if role and names and role not in lb_crew_credits:
                                lb_crew_credits[role] = names
                                # print(f'{role}:\t{names}')


                director = None
                if 'Director' in lb_crew_credits:
                    director = lb_crew_credits['Director']
                    # print(f'Director:\t{director}')
                elif 'Directors' in lb_crew_credits:
                    director = lb_crew_credits['Directors']
                    # print(f'Directors:\t{director}')
                print(director)



                # releases_link = lb_film_link + '/releases'

                # driver.get(releases_link)
                # try:
                #     WebDriverWait(driver, 5).until(
                #         EC.presence_of_element_located((By.CSS_SELECTOR, "h1.headline-1.primaryname"))
                #     )
                # finally:
                #     pass

                # soup = BeautifulSoup(driver.page_source, 'html.parser')

                # film_title = None
                # film_title_elem = soup.select_one('h1.headline-1.primaryname')
                # if film_title_elem:
                #     film_title = film_title_elem.text.strip()
                #     # print(film_title, '\n\n')


                # release_dict = {}
                # release_table_elem = soup.select_one('div#tab-releases')
                # if release_table_elem:
                #     release_type_header_elems = release_table_elem.select('h3.release-table-title')
                #     release_type_content_elems = release_table_elem.select('div.release-table.-bydate')

                #     for release_type_header_elem, release_type_content_elem in zip(release_type_header_elems, release_type_content_elems):
                #         if release_type_header_elem and release_type_content_elem:
                #             # print(release_type_header_elem, release_type_content_elem)
                #             release_type = release_type_header_elem.text.strip()

                #             release_dates = release_type_content_elem.select('h5.date')
                #             release_details = release_type_content_elem.select('span.name')

                #             release_list = []
                #             release_type_dict = {}
                #             for date_elem, details_elem in zip(release_dates, release_details):
                #                 date = date_elem.text.strip()
                #                 country = details_elem.text.strip()

                #                 release_content_str = f"{country}: {date}"
                #                 release_list.append(release_content_str)

                #                 release_type_dict[country] = date

                #             release_dict[release_type] = release_type_dict

                #             # print(f"{release_type}:\n{release_list}\n")

                # # Get earliest US theatrical release date.
                # if 'Theatrical limited' in release_dict and 'USA' in release_dict['Theatrical limited']:
                #     us_release_date = release_dict['Theatrical limited']['USA']
                # elif 'Theatrical' in release_dict and 'USA' in release_dict['Theatrical']:
                #     us_release_date = release_dict['Theatrical']['USA']
                # else:
                #     print(f"NO THEATRICAL RELEASE IN THE US FOR FILM {film_title}")
                # print(us_release_date)


            diary_record = {
                'Title': film_title,
                'Year': film_year,
                'Director': director,
                'Rating': rating,
                'Watch Date': watch_date,
                # 'Release Date': us_release_date,
            }
            diary_record_list.append(diary_record)
        
    diary_df = pd.DataFrame(diary_record_list)
    # diary_df['Watch Date'] = pd.to_datetime(diary_df['Watch Date'], format='%Y-%m-%d')
    
    testing_prefix = 'test_' if test_n_films else ''
    diary_df.to_csv(f'data/csv/{output_subdir}/{testing_prefix}lb_diary_{my_user_url}.csv', index=False)
    diary_df.to_pickle(f'data/pkl/{output_subdir}/{testing_prefix}lb_diary_{my_user_url}.pkl')

    driver.close()

    return diary_df
            


    #     # Retrieve the letterboxd links to all films on this diary page. This involves
    #     # removing the username from those links.
    #     this_pages_links = [film_entry.get_attribute('href').replace(f'/{user_url}', '') 
    #                         for film_entry in 
    #                         driver.find_elements(By.XPATH,
    #                                                 '//*[@id="diary-table"]/tbody/tr/td/h3/a')]
        
    #     # Retrieve the titles of all the films on this diary page.
    #     this_pages_film_titles = [film_entry.text for film_entry in driver.find_elements(By.XPATH, '//*[@id="diary-table"]/tbody/tr/td/h3/a')]

    #     # Retrieve their release years, too.
    #     this_pages_film_release_yrs = [year_item.text for year_item in driver.find_elements(By.XPATH, '//*[@id="diary-table"]/tbody/tr/td[4]')]

    #     # Retrieve my ratings of the films on this diary page.
    #     this_pages_ratings = [rating_item.get_attribute('aria-valuenow') for rating_item in driver.find_elements(By.CSS_SELECTOR, 'div.rateit_range')]

    #     # Add this diary page's links, titles, and release years to the corresponding
    #     # master lists.
    #     all_film_links += this_pages_links
    #     all_film_titles += this_pages_film_titles
    #     all_film_release_yrs += this_pages_film_release_yrs

    # # From the film diary lists just generated, create a dataframe, then return it.
    # letterboxd_diary_df = pd.DataFrame({'Title': all_film_titles,
    #               'Release Year': all_film_release_yrs,
    #               'Letterboxd Link': all_film_links})
    
    # # Write the dataframe of the user's film diary links to a csv file.
    # letterboxd_diary_df.to_csv(f'data/csv/{output_subdir}/lb_diary_{my_user_url}.csv', index=False)
    # letterboxd_diary_df.to_pickle(f'data/pkl/{output_subdir}/lb_diary_{my_user_url}.pkl')
    
    # return letterboxd_diary_df


if __name__ == '__main__':

    # Specify the URL segment that leads to the page of the desired user.
    my_user_url = 'yoyoyodaboy'

    # Retrieve the links in the letterboxd user's film diary, through scraping.
    users_lb_diary_df = get_users_diary_links(my_user_url)
    # users_lb_diary_df = get_users_diary_links(
    #     my_user_url,
    #     test_n_films=5,
    #     )


    # Print the dataframe (for the developer to check at a glance.)
    print('\nScraped links of Letterboxd diary entries:',
          users_lb_diary_df.head(10),
          sep='\n\n')
