from datetime import datetime

from selenium import webdriver

from bs4 import BeautifulSoup


def mc_info_scrape(film_title: str,
                         film_year: str,
                         film_link: str,
                         list_of_info_dicts: list[dict[str: str]],
                         driver: webdriver,
                         ) -> None:

    # Start the dictionary of this film's details.    
    detail_dict = {
        'Title': film_title,
        'Year': film_year,
        'Link': film_link,
    }

    # Navigate to the film's main page (on Metacritic.)
    driver.get('https://www.metacritic.com' + film_link)
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
            detail_dict['Metascore'] = metascore
            # print(film_title, 'Metascore:', metascore)

    # Summary
    summary_element = soup.select_one('span.c-productDetails_description.g-text-xsmall')
    if summary_element:
        summary = summary_element.text.strip()
        detail_dict['Summary'] = summary
        # print(film_title, summary)

    # Director(s)
    directors_element = soup.select_one('div.c-crewList.g-inner-spacing-bottom-small.c-productDetails_staff_directors').select('a.c-crewList_link.u-text-underline')
    if directors_element:
        directors_str = ' '.join([director.text.strip() for director in directors_element])
        detail_dict['Directors'] = directors_str
        # print(film_title, directors_str)

    # Writer(s)
    writers_detail_element = soup.select_one('div.c-crewList.g-inner-spacing-bottom-small.c-productDetails_staff_writers')
    # writers_element = soup.select_one('div.c-crewList.g-inner-spacing-bottom-small.c-productDetails_staff_writers').select('a.c-crewList_link.u-text-underline')
    if writers_detail_element:
        writer_entries_element = writers_detail_element.select('a.c-crewList_link.u-text-underline')
        writers_str = ' '.join([writer.text.strip() for writer in writer_entries_element])
        detail_dict['Writers'] = writers_str
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

            detail_dict['Runtime'] = runtime_in_minutes
            # print(film_title, runtime_in_minutes)

        if prod_detail_type == 'Release Date':
            release_date = elem.select_one('span.g-outer-spacing-left-medium-fluid').text.strip()
            release_date = datetime.strptime(release_date, '%b %d, %Y')
            release_date = datetime.strftime(release_date, '%Y-%m-%d')
            detail_dict['Release Date'] = release_date
            # print(film_title, release_date)

    list_of_info_dicts.append(detail_dict)