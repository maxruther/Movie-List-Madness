import requests
from bs4 import BeautifulSoup
import pymysql


# THIS SCRIPT DOESN'T WORK WELL RIGHT NOW.
#
# ISSUES:
#   - Google quickly notices the scripted querying- I get blocked after ~40
#     searches.
#
#   - The rating-scraper needs to be coded to catch the "Thumbs-down"
#     ratings. Only star ratings are yet picked up.

# Possible solutions: 
#   - Scrape with Selenium?
#   - Search through RogerEbert.com instead of Google homepage?

def google_ebert_rev_link(film_title: str, film_year: str) -> str:
    """Retrieve a link to a film's review page on RogerEbert.com , given
    the film's title and release year."""

    # (SPOTFIX) If the film's titled 'And Your Mother Too', replace that
    # with its better known title, 'Y Tu Mama Tambien'.
    if film_title == 'And Your Mother Too':
        film_title = 'Y Tu Mama Tambien'

    # Construct the search phrase
    search = f'rogerebert.com {film_title} {film_year}'

    # Set up the parameters for sending HTML requests, to request the
    # search.
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/98.0.4758.82',
    }
    parameters = {'q': search}
    
    url = 'https://www.google.com/search'

    # Send a GET request to run the search and get its results in an
    # HTML page.
    content = requests.get(url, headers=headers, params=parameters).text
    soup = BeautifulSoup(content, 'html.parser')

    # # If Google detects my scripted querying and blocks me,the following 
    # # print statement conveys their notification of this.
    # print('\n\n', soup.text, '\n\n')

    # Create a BeautifulSoup object from the bulk of the Google results
    # page.
    search = soup.find(id='search')

    # Initialize a string that might soon hold the desired link to the
    # Ebert review. Also initialize a boolean indicating whether that
    # link has been found.
    review_link = ""
    link_found = False

    # Collect the first few Google result links into an iterable.
    first_few_results = search.find_all('a', limit=3)

    # Iterate through the results to try to find a link to an Ebert
    # review of this film.
    for result in first_few_results:

        # The result's header is parsed first.
        result_header = result.text
        if result.find('h3'):
            result_header = result.find('h3').text

        # Next, its link is parsed.
        result_link = result['href']

        # # Print the result's headers and links
        # print(result_header, result_link, sep='\n', end='\n\n')

        # If the link bears the below prefix that indicates a review
        # page, and if the result's header also contains the film's
        # title, then that result is taken to be the desired result.
        if 'https://www.rogerebert.com/reviews/' in result_link:
            if f'{film_title.lower()}' in result_header.lower():
                review_link = result_link
                link_found = True

                break

    # If not link has been found, a warning is printed to the user, and
    # an empty string is returned.
    if not link_found:
        print(f'\nWARNING: Ebert review not found for',
              f'{film_title} ({film_year}\n)')
        return ""
    # Otherwise, the found link is returned.
    else:
        return review_link


def scrape_ebert_rating(ebert_review_link: str,
                        ) -> float:
    """Return the star rating (which is between 0.5 and 4) from a
    RogerEbert.com film review, given its link."""

    # If the string is empty, which indicates that no review page was
    # found, then return a '-1'.
    if not ebert_review_link:
        return -1

    # Send a GET request with the Ebert.com review link, then make a
    # BeautifulSoup object out of its HTML, to parse the review rating.
    ebert_review_page = requests.get(ebert_review_link).text
    ebert_review_soup = BeautifulSoup(ebert_review_page, 'html.parser')

    # Parse the string that contains the review rating, from the class 
    # name of the 'img' element that contains it.
    rating_str = ebert_review_soup.select_one('img.h-5').get('class')[2]

    # Only the last two characters of that string indicate the rating:
    #   - The second-to-last indicates how many full stars. 
    #   - The very last represents whether there is a half star:
    #       - 5 indicates a half-star (5 -> 0.5)
    #       - 0 indicates no half-star (0 -> 0.0)
    rating = float(rating_str[-2]) + float(rating_str[-1]) / 10

    return rating


def get_films_from_mysql_db(Cursor: pymysql.Connect.cursor,
                            ) -> list[tuple[int, str, str]]:
    """Query the index, title, and release year of all movies in my
    personal MySQL database."""

    # Query all movies' IDs, titles, and release years from the 
    # 'allmovies' table.
    query_all_titles = "SELECT Movie_ID, Title, Year FROM allmovies"
    Cursor.execute(query_all_titles)

    # From that query result, create a list and return it.
    id_titles_years_list = list(myCursor.fetchall())

    return id_titles_years_list


def gnr8_ebert_table(cursor: pymysql.Connect.cursor, 
                     ratings_data: list[int, str, str, float],
                     ) -> None:
    """Deletes then recreates the 'ebert_ratings' table of the MySQL
    movie database, populating the new table with the ratings data 
    passed."""
    
    # Delete/drop the existing 'ebert_ratings' table from the MySQL db.
    cursor.execute("DROP TABLE IF EXISTS ebert_ratings")

    # For the replacement table, programmatically construct its
    # 'CREATE TABLE' statement
    create_table_str = "CREATE TABLE IF NOT EXISTS ebert_ratings("

    # Form the SQL phrases that declare each attribute and its type.
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

    # Create the SQL clause that makes the attribute 'Movie_ID' this 
    # table's primary key.
    # create_table_str += 'FOREIGN KEY(Movie_ID) REFERENCES allmovies(Movie_ID))'
    create_table_str += 'PRIMARY KEY(Movie_ID) )'

    # # (For the dev's reference: print the final 'CREATE TABLE' string.)
    # print(create_table_str)
    
    # Execute the 'CREATE TABLE' statement, the insert all the ratings
    # data that was passed to this method.
    cursor.execute(create_table_str)
    cursor.executemany("INSERT INTO ebert_ratings VALUES (%s, %s, %s, %s)", ratings_data)


# Retrieve all films from the MySQL db, Google the links to their
# RogerEbert.com review page, then scrape their 4-star ratings from
# those pages. To finish, print them alongside the films' titles and
# release years.
if __name__ == '__main__':

    # Connect to the 'movieDB' MySQL database, then create a cursor for
    # it.
    mydb = pymysql.connect(
        host="localhost",
        user="root",
        password="yos",
        database="movieDB"
    )
    myCursor = mydb.cursor()

    # Retrieve all film records from the database. Specifically, their
    # indeces, titles, and release years.
    all_film_records = get_films_from_mysql_db(myCursor)
    print(all_film_records)

    # If this is a test run, where one prefers to run this script for
    # only a set number of films, then limit the dataset of films to
    # that many of its first film records.
    # NOTE: 'test_n_films == 0' indicates that this is not a test run.
    #       Also, if 'test_n_films' is set to a number higher than the
    #       dataset's length, then it isn't truly a test run, and
    #       'test_n_films' is duly reset to 0 to reflect this.
  
    # test_n_films = 0
    test_n_films = 10
    if test_n_films:
        if test_n_films < len(all_film_records):
            all_film_records = all_film_records[:test_n_films]
        else: 
            test_n_films = 0

    # Iterate for each film record, which are here represented as tuples
    # in the list.
    for film in all_film_records:
        title = film[1]
        year = film[2]

        ebert_review_link = google_ebert_rev_link(title, year)
        rating = scrape_ebert_rating(ebert_review_link)
        print(f'{title} ({year}): {rating}')
