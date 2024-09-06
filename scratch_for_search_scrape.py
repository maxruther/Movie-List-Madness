import requests
from bs4 import BeautifulSoup
import pymysql

film_title = 'oddity'
film_year = '2024'


def google_ebert_rev_link(film_title, film_year):
    if film_title == 'And Your Mother Too':
        film_title = 'Y Tu Mama Tambien'

    search = f'rogerebert.com {film_title} {film_year}'
    url = 'https://www.google.com/search'

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/98.0.4758.82',
    }
    parameters = {'q': search}

    content = requests.get(url, headers=headers, params=parameters).text
    print(content)
    soup = BeautifulSoup(content, 'html.parser')

    search_results = soup.find(id='search')
    first_five_results = soup.find_all('h3')
    # print(content)
    # first_link = search_results.find('a')
    print(first_five_results)

    review_link = ""
    link_found = False

    # first_five_results = soup.find_all('h3', limit=5)
    print(first_five_results)
    for result in first_five_results:
        print(result)
        print(result.text)
        print('\n\n')

        result_header = result.text
        if result.find('h3'):
            result_header = result.find('h3').text

        result_link = result['href']
        # Print result headers and links
        # print(result_header, result_link, sep='\n', end='\n\n')

        if 'https://www.rogerebert.com/reviews/' in result_link:
            # if f'{film_title.lower()}' in result_header.lower() and 'movie review' in result_header.lower():
            if f'{film_title.lower()}' in result_header.lower():
                review_link = result_link
                link_found = True
                # print("EBERT REVIEW FOUND: ")
                # print(result_header, result_link, sep='\n', end='\n\n')
                break

    if not link_found:
        print(f'Ebert review not found for {film_title} ({film_year})')
        return ""
    else:
        return review_link

print(google_ebert_rev_link("The Ascent", "1977"))