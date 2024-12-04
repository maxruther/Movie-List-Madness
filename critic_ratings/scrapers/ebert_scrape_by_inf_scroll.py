import re
import requests
from bs4 import BeautifulSoup
import pandas as pd


"""
THIS METHOD DOESN'T WORK RIGHT NOW.

ISSUE:
    - The infinite-scroll of this scrape isn't working, a method I found 
      online. Only the first page of reviews is getting processed.

OTHER TASKS:
    - When a movie from this grid bears a rating of 3.5+ stars, follow
      that link and get more information about it.
"""

def scrape_ebert_review_page(num_pages=1):
    """
    Parses through RogerEbert.com's page of all reviews, which expands
    as one scrolls down it, and returns a DataFrame of movie scores
    therein.
    num_pages = Number of pages to scroll through.
    """
    # url = "https://www.rogerebert.com/reviews"
    url = ('http://www.rogerebert.com/reviews?great_movies=0&no_stars=0'
           '&title=Cabin+in+the+Woods&filtersgreat_movies%5D%5B%5D=&fil'
           'ters%5Bno_stars%5D%5B%5D=&filters%5Bno_stars%5D%5B%5D=1&fil'
           'ters%5Btitle%5D=&filters%5Breviewers%5D=&filters%5Bgenres%5'
           'D=&page={}&sort%5Border%5D=newest')
    
    # Create a list of integers signifying how many pages of 
    # infinite-scroll you would like to scrape.
    pages = list(range(1, num_pages + 1))

    # From those page numbers, create a list of corresponding URL's.
    links = [url.format(i) for i in pages]

    # Initialize two lists: one to contain all reviews and the other to
    # only contain hits.
    review_list = []
    ebert_hits = []

    for i, link in enumerate(links):
        # print(f'PAGE #{i}', link)
        webpage = requests.get(link).text

        soup = BeautifulSoup(webpage, "html.parser")

        table_names = []
        all_movies = soup.select('article.review-small-card')
        for movie in all_movies:
            title = movie.select_one('h3.text-2xl').span.text.strip()
            critic = movie.select_one('div.montserrat-500').text.strip()
            
            rating_str = movie.select_one('img.h-5').get('class')[2]
            rating = float(rating_str[-2]) + float(rating_str[-1]) / 10

            print(title, rating, critic, sep='\t')

            if rating >= 3.5:
                  review_link = movie.select_one('a.image-hover').get('href')
                #   print(review_link)
                  review_page = requests.get(review_link).text
                #   print(review_page)
                  review_soup = BeautifulSoup(review_page, 'html.parser')

                  # title_and_year = review_soup.select_one('h4.page-title').text
                  # # Parse the film's title and year from the retrieved string comprised of both.
                  # pattern = r'(^.+\S)\s+\((\d{4})\)$'
                  # print(title_and_year)
                  # title, year = re.search(pattern, title_and_year).groups()
                  genre = review_soup.select_one('a.px-2').text
                  runtime_mpa_year = review_soup.select_one('div.mt-4').text.split('‧')
                  runtime_mpa_year = [x.strip() for x in runtime_mpa_year]
                  runtime, mpa, year = runtime_mpa_year

                  hit_record_dict = {'Title': title,
                                     'Year': year,
                                     'Rating': rating,
                                     'Critic': critic,
                                     'Genre': genre,
                                     'Runtime': runtime,
                                     'MPA': mpa
                                     }

                  print(list(hit_record_dict.values()))
                  
                  ebert_hits.append(hit_record_dict)

    df = pd.DataFrame(review_list, columns=['Title', 'EbertStars', 'Year', 'URL'])

    ebert_hits_df = pd.DataFrame(ebert_hits)

    return df, ebert_hits_df


if __name__ == '__main__':
    review_df, ebert_hits_df = scrape_ebert_review_page()
    print(ebert_hits_df)

    ebert_hits_df.to_csv('data/scraped/ebert_recent_hits.csv')