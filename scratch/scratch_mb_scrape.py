from selenium import webdriver
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

import pandas as pd

import time
from datetime import datetime
import re

import pickle


def tech_summary_list_to_dict(tech_summary_list: list[str],
                              ) -> dict[str: int | str]:

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


options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Chrome(options)

with open('mb_calendar_text.pkl', 'rb') as file:
    calendar_text = pickle.load(file)

soup = BeautifulSoup(calendar_text, 'html.parser')

# calendar_days = soup.select('div.Item')
# calendar_days = soup.select('td.InsideDate', limit=1)
calendar_days = soup.select('div.calendar-cell')

films_showtimes = {}
film_details = {}

mb_series_list = [
    # 'Music Box Movie Trivia',
    # 'Strange and Found',
    ]

for day in calendar_days:
# for day in calendar_days[27:32]:
    # print(day.get('class'))
    if 'calendar-head' in day.get('class'):
        print('EMPTY CALENDAR CELL - HEADER')
    elif 'empty' in day.get('class'):
        print('EMPTY CALENDAR CELL - PAST DATE')
    else:
        calendar_date_elem = day.select_one('div.calendar-date')
        date_text_all = calendar_date_elem.text.strip().split(', ')
        date_str = ' '.join(date_text_all[-2:])

        day_datetime = datetime.strptime(date_str, '%b %d %Y')
        # print(f'\n\n{day_datetime}\n')
        # print(f'\n\n{date_str}\n')

    
    shows = day.select('div.programming-content')
    for show in shows:

        show_title = show.select_one('a').text.strip()

        # Remove parenthesized release year from the show/film title string.
        pattern = r'(.*)\ \((\d{4})\)$'
        if re.search(pattern, show_title):
            show_title = re.search(pattern, show_title).groups()[0]

        show_tags = show.select_one('div.tags').text.strip()
        if show_tags:
            # print(f'{show_title.upper()} | {show_tags}:')

            """
            # Series Handling
            if show_tags == 'Film Series':
                series_relative_link = show.select_one('a').get('href')
                print(series_relative_link)
                series_link = 'https://musicboxtheatre.com' + series_relative_link
                driver.get(series_link)
            """


        # else:
            # print(f'{show_title.upper()}:')

        showtimes_elem = show.select_one('div.programming-showtimes')

        if showtimes_elem:

            if show_title not in film_details:
                if show_title not in mb_series_list:
                    show_rel_link = show.select_one('a').get('href')
                    show_link = 'https://musicboxtheatre.com' + show_rel_link
                    # print(show_link)
                    driver.get(show_link)
                    main_section_xpath = '/html/body/div[1]/main'
                    main_section_text = driver.find_element(By.XPATH, value=main_section_xpath).get_attribute('innerHTML')
                    main_section_soup = BeautifulSoup(main_section_text, 'html.parser')

                    tech_summary_elem = main_section_soup.select_one('p.tech-summary')
                    tech_summ_deets = tech_summary_elem.select('span')
                    tech_deet_list = [deet.text.strip() for deet in tech_summ_deets]
                    film_details[show_title] = tech_summary_list_to_dict(tech_deet_list) 
                    # print(tech_deet_list)
                    # print(tech_summary_elem.text)
                    # for deet in tech_summ_deets:
                    #     print(deet.text.strip())

                    

            showtimes = showtimes_elem.select('a.use-ajax')
            # print(f'Showtimes:')
            for showtime in showtimes:
                showtime_str = showtime.text.replace('"', '')

                date_and_showtime = date_str + ' ' + showtime_str
                showtime_datetime = datetime.strptime(date_and_showtime, 
                                                      '%b %d %Y %I:%M%p')
                # print(showtime_datetime)

                if show_title not in films_showtimes:
                    films_showtimes[show_title] = [showtime_datetime]
                else:
                    if showtime_datetime not in films_showtimes[show_title]:
                        films_showtimes[show_title].append(showtime_datetime)



        # print()


for pair in film_details.items():
    print(pair)
print()

print(films_showtimes, '\n\n')
print(film_details)

film_details_df = pd.DataFrame.from_dict(film_details, orient='index').reset_index()
film_details_df.rename(columns={'index': 'Title'}, inplace=True)
print(film_details_df)

with open('musicbox_films_showtimes_dict.pkl', 'wb') as file:
    pickle.dump(films_showtimes, file)

with open('musicbox_film_details_dict.pkl', 'wb') as file:
    pickle.dump(film_details, file)

# # (For the dev's reference) print the runtime of the scrape.
# scrape_runtime = time.time() - scrape_start
# scrape_runtime = round(scrape_runtime)
# runtime_min = scrape_runtime // 60
# runtime_sec = scrape_runtime % 60
# scrape_runtime_str = f'{runtime_min} m {runtime_sec} s'
# print(f'\nRuntime of this scrape: {scrape_runtime_str}')


driver.close()