from selenium import webdriver
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
import re

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz


def mc_get_films_link(
        film_title: str,
        film_year: str,
        film_director: str,
        list_of_searchresult_dicts: list[dict[str: str]],
        driver: webdriver,
):
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
            
            # If the release year of the searched film sufficently 
            # matches that of a result, that result is considered a top 
            # candidate. As such, its similarities to the searched title
            # (and its link) are stored in a dictionary for later 
            # comparison to the others.
            if abs(int(result_year) - int(film_year)) <= 1 or title_cos_sim == 1:
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
                        # print(f'{film_title} {film_director} {result_director}')
                        director_vectors = vectorizer.fit_transform([film_director.lower(), result_director.lower()])
                        director_cos_sim = cosine_similarity(director_vectors[0], director_vectors[1])[0][0]
                        director_cos_sim = round(director_cos_sim, 3)

                        director_fuzzy_sim = fuzz.ratio(film_director.lower(), result_director.lower())
                        director_fuzzy_sim = round(director_fuzzy_sim / 100, 3)

                        # print(f'{film_title} ({film_year}) Director similarities:',
                        #     f'{film_director}\t{result_director}',
                        #     f'Fuzzy sim. = {director_fuzzy_sim}\nCosine sim. = {director_cos_sim}',
                        #     sep='\n', end='\n\n')
                
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
                list_of_searchresult_dicts.append(search_result_dict)

                # If the search result's title and director are (cosine) similar
                # at 1, then it is chosen as the match and the remaining search
                # results are skipped.
                if title_cos_sim == 1 and director_cos_sim == 1:
                    perfect_result_not_found = False
    
    # With the results' examination now complete, the single-most
    # similar search result is chosen.
    if len(top_results) == 1:
        # If there is only one result that might fit.
        result_title, result_dict = top_results.popitem()

        result_year = result_dict['Year Result']

        # If the searched film's director is known, use its similarity 
        # to the result's to determine selection.
        if film_director:
            if result_dict['Titles Cosine Sim'] == 1 and result_dict['Directors Cosine Sim'] >= 0.5:
                chosen_link = result_dict['Link']
            elif result_dict['Titles Cosine Sim'] < 1:
                if result_dict['Directors Cosine Sim'] >= 0.5:
                    chosen_link = result_dict['Link']
        # If the director is not known
        else:
            if result_dict['Titles Cosine Sim'] == 1 and abs(int(result_year) - int(film_year)) <= 1:
                chosen_link = result_dict['Link']

        
        if not chosen_link:
            print("NO METACRITIC PAGE IDENTIFIED for film",
                    f'"{film_title} ({film_year})":',
                    "\nOne search result showed a similar year, but its",
                    "title and/or director(s) were too dissimilar to",
                    "indicate a match.\n")
            
            # Add a record to signify that this film's page was searched for (with 
            # the given title, year, and director.)
            list_of_searchresult_dicts.append({
                    'Title Searched': film_title,
                    'Year Searched': film_year,
                    'Director Searched': film_director,
                })

    elif len(top_results) > 1:
        # If there are multiple results to decide from, then the one
        # with the highest 'fuzzy' similiarity to the searched title is
        # chosen.
        max_fuzzy_sim = 0
        chosen_result_dict = {}
        for result in top_results:
            if top_results[result]['Titles Fuzzy Sim'] > max_fuzzy_sim:
                chosen_result_dict = top_results[result]
                max_fuzzy_sim = top_results[result]['Titles Fuzzy Sim']

        result_year = chosen_result_dict['Year Result']

        # if test_n_films:
        #     print(f'\n\n{film_title_and_year}\n{top_results}\n')
        
        # If the result's title and director are (cosine) similar enough
        # to those of the searched film, then it is chosen as the match.
        if chosen_result_dict['Titles Cosine Sim'] == 1:
            # Scrutinize further if director similarity is available.
            if film_director:
                if chosen_result_dict['Directors Cosine Sim'] >= 0.5:
                    chosen_link = chosen_result_dict['Link']
            # Otherwise, just choose this result.
            else:
                if chosen_result_dict['Titles Cosine Sim'] == 1 and abs(int(result_year) - int(film_year)) <= 1:
                    chosen_link = chosen_result_dict['Link']
        
        elif chosen_result_dict['Titles Cosine Sim'] < 1:
            if film_director:
                if chosen_result_dict['Directors Cosine Sim'] >= 0.5:
                    chosen_link = chosen_result_dict['Link']
            else:
                if chosen_result_dict['Titles Cosine Sim'] > 0.66:
                    chosen_link = chosen_result_dict['Link']
        
        if not chosen_link:
            print("NO METACRITIC PAGE IDENTIFIED for film",
                      f"{film_title} ({film_year}).",
                      "\nMultiple search results showed a similar year or",
                      "a closely matching title, but either their",
                      "titles or directors were too dissimilar to",
                      "indicate a match.\n")
        
            # Add a record to signify that this film's page was searched for (with 
            # the given title, year, and director.)
            list_of_searchresult_dicts.append({
                    'Title Searched': film_title,
                    'Year Searched': film_year,
                    'Director Searched': film_director,
                })

        
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
        
        # Add a record to signify that this film's page was searched for (with 
        # the given title, year, and director.)
        list_of_searchresult_dicts.append({
                'Title Searched': film_title,
                'Year Searched': film_year,
                'Director Searched': film_director,
            })
    
    return chosen_link