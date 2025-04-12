import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

import pandas as pd
from os import makedirs

from utils import create_chromedriver, save_output_df_to_dirs


def lb_scrape_diary(
        user_url: str = 'yoyoyodaboy',
        output_subdir: str = 'letterboxd',
        test_n_films: int = 0,
        ) -> list[str]:
    
    # # Set up the Selenium Chromium driver
    # options = webdriver.ChromeOptions()
    # options.add_argument('--ignore-certificate-errors')
    # options.add_argument('--ignore-ssl-errors')
    # # options.page_load_strategy = 'eager'
    # options.page_load_strategy = 'none'

    # driver = webdriver.Chrome(options)

    # Set up the Selenium Chromium driver
    driver = create_chromedriver('none')
    driver.implicitly_wait(3)

    # Navigate to user's film diary page.
    driver.get(f"https://letterboxd.com/{user_url}/films/diary/")

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 'div#content'))
        )
    finally:
        pass

    # From that page, retrieve the diary's page count.
    # diary_pages_xpath = '//*[@id="content"]/div/section[2]/div[2]/div[3]/ul/li/a'
    # diary_page_elems = driver.find_elements(By.XPATH, diary_pages_xpath)
    diary_page_elems = driver.find_elements(
        By.CSS_SELECTOR, 
        'li.paginate-page'
        )
    diary_page_count = int(diary_page_elems[-1].text.strip())

    # Initialize the list that will hold the watched films' records, 
    # which are dictionaries.
    diary_record_list = []


    # # Scrape each page of the film diary for that information.
    # (If testing, only process the first page of the diary.)
    if test_n_films:
        diary_page_count = 1
    for i in range(1, diary_page_count + 1):
        # Navigate to the i-th diary page.
        diary_page_link = f'https://letterboxd.com/{user_url}/films/diary/page/{str(i)}/'
        driver.get(diary_page_link)

        # Have the driver wait until the element of interest appears on
        # the diary page. This waiting actually helps cut down on
        # runtime, as the driver otherwise waits for everything on page
        # to load (including ads, which can be videos.)
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div#content-nav"))
            )
        finally:
            pass

        # Create a BeautifulSoup object from the page's html, to parse
        # the film-watch entries that make up the diary page.
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        diary_entry_elems = soup.select('tr.diary-entry-row')

        # Iterate through each diary entry. (If testing, only iterate
        # through <test_n_films> entries.)
        if test_n_films:
            if test_n_films < len(diary_entry_elems):
                diary_entry_elems = list(diary_entry_elems)[:test_n_films]
        for entry_elem in diary_entry_elems:

            # Film title
            film_title = None
            film_title_elem = entry_elem.select_one('td.td-film-details')
            if film_title_elem:
                film_title_header_elem = film_title_elem.select_one('h3')
                if film_title_header_elem:
                    film_title = film_title_header_elem.text.strip()
                    # print(film_title)

            # Film year
            film_year = None
            film_year_elem = entry_elem.select_one('td.td-released')
            if film_year_elem:
                film_year = film_year_elem.text.strip()
                # print(film_year)

            # The user's rating of the film. Letterboxd ratings range
            # between 0-5 stars, and half-stars can be given (e.g. 
            # 4.5 stars)
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
                # print(rating)

            # Watch Date
            watch_date = None
            watch_date_elem = entry_elem.select_one('td.td-day.diary-day')
            if watch_date_elem:
                watch_date_link_elem = watch_date_elem.select_one('a')
                if watch_date_link_elem:
                    watch_date_link = watch_date_link_elem.get('href')
                    watch_date = '-'.join(watch_date_link.split('/')[-4:-1])
                    # print(watch_date)
            
            # Link to the film's dedicated page on Letterboxd
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
                        # print(lb_film_link)


            # If a link to the film's dedicated Letterboxd page was
            # successfully retrieved, navigate to that page to retrieve
            # the film's director. (US release date retrieval is still
            # in the works.)
            director, us_release_date = None, None
            if lb_film_link:

                crew_link = lb_film_link + '/crew'

                # Navigate to the flim's 'crew' page and load it until
                # the element containing the crew credits has loaded.
                driver.get(crew_link)
                try:
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.tabbed-content-block.column-block.-crewroles"))
                    )
                except:
                    raise Exception("ERROR: The crew element of the film's crew",
                          "page failed to load in time.",
                          f"\nFilm: {film_title} ({film_year})")

                # Create a dictionary to hold all of this film's crew
                # credits.
                lb_crew_credits = {}

                crew_soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Within the crew credits element, parse the parallel
                # 'h3' and 'div' elements that correspond with the names
                # of the crew roles and those credited, respectively.
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
                                names = ', '.join(name_list)
                                # print(names)

                            if role and names and role not in lb_crew_credits:
                                # Add the new crew credit to the
                                # dictionary.
                                lb_crew_credits[role] = names
                                # print(f'{role}:\t{names}')

                # # Director
                # Retrieve the director from the film's crew credit
                # dictionary, if available.
                director = None
                if 'Director' in lb_crew_credits:
                    director = lb_crew_credits['Director']
                elif 'Directors' in lb_crew_credits:
                    director = lb_crew_credits['Directors']
                # print(director)

            # Create this diary entry's record from the data scraped
            # above.
            diary_record = {
                'Title': film_title,
                'Year': film_year,
                'Director': director,
                'Rating': rating,
                'Watch Date': watch_date,
                'LB_Film_Link': lb_film_link, # This field is crucial to 'lb_scrape_friends_ratings.py'
                # 'Release Date': us_release_date,
            }
            diary_record_list.append(diary_record)
    
    # Form a dataframe from the scraped diary data.
    diary_df = pd.DataFrame(diary_record_list)
    # diary_df['Watch Date'] = pd.to_datetime(diary_df['Watch Date'], format='%Y-%m-%d')

    # Save this output dataframe to csv and pkl files.
    output_filename = f'lb_diary_{user_url}'

    save_output_df_to_dirs(
        diary_df,
        test_n_films,
        output_filename,
        output_subdir,
        )

    driver.close()

    return diary_df


if __name__ == '__main__':

    # Specify the URL segment that leads to the page of the desired user.
    user_url = 'yoyoyodaboy'

    # Retrieve the links in the letterboxd user's film diary, through scraping.
    # users_lb_diary_df = lb_scrape_diary(user_url, test_n_films=3)
    users_lb_diary_df = lb_scrape_diary(user_url)


    # Print the dataframe (for the developer to check at a glance.)
    print('\nScraped links of Letterboxd diary entries:',
          users_lb_diary_df.head(10),
          sep='\n\n')
