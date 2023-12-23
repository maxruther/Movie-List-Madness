from bs4 import BeautifulSoup
import mysql.connector


# Here we read in the movie list HTML content, by using it to create a
# BeautifulSoup object.
movieFile = "Movies\Movies.html"
with open(movieFile) as f:
    soup = BeautifulSoup(f, "html.parser")

# Here we read in the names of each of the tables, which are identified
# by their being 'h2' elements.
# NOTE: Any 'h2' headings in the Evernote movie list will be added as
# table headers, which could really mess things up.
header_counter = 0
table_headers = []
allHeaders = soup.find_all(name="h2")

# Removing first header, as it's the "In Theaters: " header, which
# doesn't one of the tables.
allHeaders.pop(0)

# The table names
for header in allHeaders:
    header_name = header.text[0:-1].replace(" ", "_") + "_og"
    table_headers.append()

print(table_headers)
