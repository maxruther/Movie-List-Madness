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
    soup = BeautifulSoup(content, 'html.parser')

    search = soup.find(id='search')
    # first_link = search.find('a')
    # print(first_link['href'])

    review_link = ""
    link_found = False

    first_five_results = search.find_all('a', limit=3)
    for result in first_five_results:
        # print(result)
        # print(result.text)
        # print('\n\n')

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


def scrape_ebert_rating(ebert_review_link):
    if not ebert_review_link:
        return -1

    ebert_review_page = requests.get(ebert_review_link).text
    ebert_review_soup = BeautifulSoup(ebert_review_page, 'html.parser')

    star_rating_element = ebert_review_soup.find('span', class_='star-rating _large')
    full_star_count = len(star_rating_element.find_all('i', {'title': 'star-full'}))
    half_star_count = len(star_rating_element.find_all('i', {'title': 'star-half'}))
    # print(f'{full_star_count=}', f'{half_star_count=}')

    complete_star_rating = full_star_count + half_star_count / 2

    # print(complete_star_rating)
    return complete_star_rating


def get_film_titles_and_years(Cursor, num_films=10):
    keyFile = "C:/Users/maxru/Programming/Python/.secret/OMDB_API.txt"

    with open(keyFile) as f:
        API_key = f.read()

    query_all_titles = "SELECT Movie_ID, Title, Year FROM allmovies"
    Cursor.execute(query_all_titles)

    titles_years_list = list(myCursor.fetchall())
    # counter = 0
    # for (Movie_ID, Title, Year) in Cursor:
    #     titles_years_list.append((Title, Year))
    #
    #     counter += 1
    #     if counter == num_films - 1:
    #         break

    return titles_years_list


def gnr8_ebert_table(cursor, ratings_data):
    cursor.execute("DROP TABLE IF EXISTS ebert_ratings")

    create_table_str = "CREATE TABLE IF NOT EXISTS ebert_ratings("

    col_names = ['Movie_ID', 'Title', 'Year', 'Ebert_Score']
    num_cols = len(col_names)
    for i in range(num_cols):
        curr_attr = col_names[i]
        var_type = " varchar(80)"

        if "Score" in curr_attr:
            var_type = " float"
        elif "Movie_ID" in curr_attr:
            var_type = " int NOT NULL"

        create_table_str += curr_attr + var_type + ', '

    # create_table_str += 'FOREIGN KEY(Movie_ID) REFERENCES allmovies(Movie_ID))'
    create_table_str += 'PRIMARY KEY(Movie_ID) )'
    # print(create_table_str)
    cursor.execute(create_table_str)

    cursor.executemany("INSERT INTO ebert_ratings VALUES (%s, %s, %s, %s)", ratings_data)

mydb = pymysql.connect(
    host="localhost",
    user="root",
    password="yos",
    database="movieDB"
)

myCursor = mydb.cursor()

all_film_records = get_film_titles_and_years(myCursor)
print(all_film_records)

for film in all_film_records:
    title = film[1]
    year = film[2]
    rating = scrape_ebert_rating(google_ebert_rev_link(title, year))
    print(f'{title} ({year}): {rating}')
