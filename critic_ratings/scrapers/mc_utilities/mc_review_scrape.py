from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import os

if __name__ == '__main__':
    from select_text_from_soup import select_text_from_soup
else:
    try:
        from mc_utilities.select_text_from_soup import select_text_from_soup
    except:
        try:
            from critic_ratings.scrapers.mc_utilities.select_text_from_soup import select_text_from_soup
        except:
            raise Exception(f"ERROR - {os.path.basename(__file__)}: Failed to import method 'select_text_from_soup'.")

def mc_review_scrape(title_searched: str,
                     year_searched: str,
                     film_link: str,
                     list_of_review_dicts: list[dict[str: str]],
                     driver: webdriver,
                     director_searched: str = None,
                     ) -> None:
    
    film_review_link = f'https://www.metacritic.com' + film_link + \
            'critic-reviews/'
    driver.get(film_review_link)

    fullpage_source = driver.page_source
    soup = BeautifulSoup(fullpage_source, 'html.parser')
                        

    review_cnt = None
    review_cnt_elem = soup.select_one('div.c-pageProductReviews_text')
    if review_cnt_elem:
        review_cnt_text = review_cnt_elem.text.strip()
        pattern = 'Showing (\d+) Critic Reviews'
        match = re.match(pattern, review_cnt_text)
        if match:
            review_cnt = match.group(1)

    reviews_xpath = '//*[@id="__layout"]/div/div[2]/div[1]/' \
        + 'div[1]/section/div[4]/div/div'
    
    review_texts = driver.find_elements(By.XPATH, 
                                        reviews_xpath)
    
    # Define a dictionary of the various data elements sought
    # and their corresponding CSS selector strings.
    css_sel_strs = {
        'Publication': 'a.c-siteReviewHeader_publicationName',
        'Score': 'div.c-siteReviewScore' \
            + ':not(.c-siteReviewScore_background)',
        'Critic': '.c-siteReview_criticName',
        'Snippet': 'div.c-siteReview_quote',
        'Date Written': 'div.c-siteReviewHeader_reviewDate',
    }

    # Iterate through each critic review of this film.
    for review_text in review_texts:

        # Initialize this critic review's data dictionary as only
        # containing the film's title.
        cr_dict = {
            'Title Searched': title_searched,
            'Year Searched': year_searched,
            'Director Searched': director_searched,
            }

        # Create a BeautifulSoup object from this review.
        soup = BeautifulSoup(review_text.get_attribute('innerHTML'), 
                            'html.parser')

        # For each of desired attribute and corresponding 
        # CSS-selector string, retrieve and enter this critic 
        # review's data into the dictionary. 
        for attr, css_str in css_sel_strs.items():
            value = select_text_from_soup(attr, soup, css_str)
            cr_dict.update({attr: value})

        # If the 'Critic' value is prefixed with the phrase 'By ' 
        # (as it tends to be) then remove that prefix.
        critic_name = cr_dict['Critic']
        if len(critic_name) >= 3:
            if critic_name[:3] == 'By ':
                cr_dict['Critic'] = critic_name[3:]
        
        # Add this critic review's data dictionary to their list.
        list_of_review_dicts.append(cr_dict)

    scrape_success_str = f"\tCritic reviews successfully scraped"
    if review_cnt:
        scrape_success_str += f", {review_cnt} in total."
    else:
        scrape_success_str += "."
    print(scrape_success_str)
