from bs4 import BeautifulSoup

fileName = "Movies/Movies.html"

with open(fileName) as f:
    soup = BeautifulSoup(f, "html.parser")

    # Here we read in the names of each of the tables, which are identified
    # by their being 'h2' elements.
    # NOTE: Any 'h2' headings in the Evernote movie list will be added as
    # table headers, which could really mess things up.
table_names = []
allHeaders = soup.find_all(name="h2")

# Removing first header, as it's the "In Theaters" header, which
# doesn't have a table associated.
allHeaders.pop(0)

# The rest of the headers in this Evernote file are table names. Taking
# the text of these headers, reformatting them, then appending them to
# a list of table names.
for header in allHeaders:
    header_name = header.text[0:-1].replace(" ", "_") + "_og"
    table_names.append(header_name)

# Reading in all of the tables.

# Data will be a 3D list. For each table, it will hold a corresponding 2D
# list.
data = []
table_ind = 0
movie_id = 1
movie_dict = {}
for table in soup.find_all("en-table"):
    # Each table is read into a 2D list. The first 1D list contained will
    # only contain the table's name, while the rest will hold the table's
    # data.
    curr_table = [[table_names[table_ind]]]
    table_ind += 1
    row_num = 0
    # Each row of the table is iterated through, where individual
    # elements are indicated by <td> objects.
    for row in table.find_all("tr"):
        curr_row = []
        dataElements = row.find_all("td")
        for element in dataElements:
            curr_elem = element.text

            # This 'liFound' block handles the 'Watched' column intake,
            # which is a checkbox value in Evernote.
            liFound = element.find("li")
            if liFound:
                # If an <li> object shows 'True' for its 'data-checked'
                # value, that indicates that it's a checkbox.
                if liFound["data-checked"] == "true":
                    curr_elem = 1
                else:
                    curr_elem = 0

            # If the current element is blank, it is recorded as 'NULL'
            # in the data, for SQL.
            elif curr_elem == '':
                curr_elem = "NULL"

            # Following is some string handling. Values that contain
            # a single-quote character are enclosed in double-quotes
            # (and vice versa) for easy insertion into SQL tables.
            elif isinstance(curr_elem, str):
                if row_num > 0:
                    if "'" in curr_elem:
                        curr_elem = '"' + curr_elem + '"'
                    else:
                        curr_elem = "'" + curr_elem + "'"

                # Column header strings are here reformatted, to better
                # serve as field names in SQL.
                elif row_num == 0:
                    curr_elem = curr_elem.replace(" ", "_")
                    curr_elem = curr_elem.replace("Awesome?", "Rating")

            # Having been prepped, the element is appended to the row's
            # list, then that row is appended to the 2D table-list once
            # complete.
            curr_row.append(curr_elem)
        if row_num == 0:
            curr_row = ['Movie ID'] + curr_row
        else:
            curr_row = [movie_id] + curr_row
            movie_dict[curr_row[1] + curr_row[2]] = movie_id
            movie_id += 1

        curr_table.append(curr_row.copy())
        row_num += 1

    # A copy of that table's data is then appended to the Data list.
    data.append(curr_table.copy())

print(data[2][0:4])
