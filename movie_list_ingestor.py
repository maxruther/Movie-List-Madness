from bs4 import BeautifulSoup
# import mysql.connector
import pymysql


def evernote_2_3d_pylist(file_name):
    # Here we read in the movie list HTML content, by using it to create a
    # BeautifulSoup object.
    with open(file_name, errors='ignore') as f:
        soup = BeautifulSoup(f, "html.parser")

    # Here we read in the names of each of the tables, which are identified
    # by their being 'h2' elements.
    # NOTE: Any 'h2' headings in the Evernote movie list will be added as
    # table headers, which could really mess things up.
    table_names = []
    all_h2_headers = soup.find_all(name="h2")

    # Removing first header, as it's the "In Theaters" header, which
    # doesn't have a table associated.
    # EDIT: NEVER MIND - I've deleted this "In Theaters" header.
    # all_h2_headers.pop(0)

    # The rest of the headers in this Evernote file are table names. Taking
    # the text of these headers, reformatting them, then appending them to
    # a list of table names.
    for header in all_h2_headers:
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
        # print(table_names, table_ind, sep='\n')
        curr_table = [[table_names[table_ind]]]
        table_ind += 1
        row_num = 0
        # Each row of the table is iterated through, where individual
        # elements are indicated by <td> objects.
        for row in table.find_all("tr"):
            curr_row = []
            data_elements = row.find_all("td")
            for element in data_elements:
                curr_elem = element.text

                # This 'li_found' block handles the 'Watched' column intake,
                # which is a checkbox value in Evernote.
                li_found = element.find("li")
                if li_found:
                    # If an <li> object shows 'True' for its 'data-checked'
                    # value, that indicates that it's a checkbox.
                    if li_found["data-checked"] == "true":
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
                curr_row = ['Movie_ID'] + curr_row
            else:
                title_and_dir = curr_row[0] + curr_row[1]
                if movie_dict.get(title_and_dir, -1) == -1:
                    curr_row = [movie_id] + curr_row
                    movie_dict[title_and_dir] = movie_id
                    movie_id += 1
                else:
                    curr_row = [movie_dict.get(title_and_dir)] + curr_row

            curr_table.append(curr_row.copy())
            row_num += 1

        # A copy of that table's data is then appended to the Data list.
        data.append(curr_table.copy())

    return data


# Clearing and deleting an existing table
def delete_from_table_stmt(k, data):
    table_name = data[k][0][0]
    delete_table_str = "DELETE FROM " + table_name
    return delete_table_str


# Dropping a table if it exists
def drop_table_stmt(k, data):
    table_name = data[k][0][0]
    drop_table_str = "DROP TABLE IF EXISTS " + table_name
    return drop_table_str


# Creating a table
def create_table_stmt(k, data):
    table_name = data[k][0][0]
    table_attrs = []
    for attr in data[k][1]:
        table_attrs.append(attr)

    num_attrs = len(table_attrs)
    create_table_str = "CREATE TABLE IF NOT EXISTS " + table_name + "("

    # Collecting the tables attributes into a list of strings
    crt_tbl_attrs = []
    for i in range(num_attrs):
        curr_attr = table_attrs[i]
        var_type = " varchar(80)"

        if curr_attr in ["Watched", "Movie_ID"]:
            var_type = " int"
        elif "Date" in curr_attr:
            var_type = " date"

        crt_tbl_attrs.append(curr_attr + var_type + ", ")

    crt_tbl_attrs.append("native_ordering int NOT NULL UNIQUE)")

    # Construct the "CREATE TABLE" statement, though it lacks constraints.
    for i in crt_tbl_attrs:
        create_table_str += i

    # Adding constraints as necessary
    constraint_strings = []
    if "Movie_ID" in table_attrs:
        constraint_strings.append("PRIMARY KEY (Movie_ID)")
    if "Watched" in table_attrs:
        constraint_strings.append("CHECK (Watched in (0, 1))")
    if "Watched_in_theater" in table_attrs:
        constraint_strings.append("CHECK (Watched_in_theater in (0, 1))")
    if len(constraint_strings) > 0:
        total_constraint_str = ", ".join(constraint_strings)
        total_constraint_str = total_constraint_str + ")"
        create_table_str = create_table_str[:-1] + ", " + total_constraint_str

    # print(create_table_str)
    return create_table_str


def table_insert_queries(k):
    insert_stmts = []
    native_index = 1
    for i in range(2, len(ingested_movie_data[k])):
        ins_vals_str = "INSERT INTO " + ingested_movie_data[k][0][0] + " VALUES("
        if i < 2:
            continue
        vals = ingested_movie_data[k][i]

        # print(data[k])
        # for val in vals:
        for l in range(len(vals)):
            val = vals[l]

            # Checking if it's a date, then replacing "/" chars if so.
            date_test_val = str(val).replace("/", "").replace("'", "")
            if "Date" in ingested_movie_data[k][1][l] and "NULL" not in date_test_val:
                # if date_test_val.isnumeric() and len(date_test_val) > 1:
                the_date = val.replace("'", "").split("/")
                # print(the_date)
                mon = the_date[0]
                day = the_date[1]
                yr = the_date[2]
                if len(yr) < 4:
                    if 50 <= int(yr) <= 99:
                        yr = "19" + yr
                    else:
                        yr = "20" + yr
                val = "'" + yr + "-" + mon + "-" + day + "'"

            if l < len(vals) - 1:
                ins_vals_str += str(val) + ", "
            else:
                ins_vals_str += str(val) + ", " + str(native_index) + ")"
                native_index += 1
        insert_stmts.append(ins_vals_str)

    return insert_stmts


def recreate_tables_with_data(the_data, a_cursor, a_DB):
    # Recreating and loading up the various tables
    for i in range(len(the_data)):
        a_cursor.execute(drop_table_stmt(i, the_data))
        # If an Evernote table has unnamed columns, it will cause errors
        # here.
        # print(create_table_stmt(i, the_data))
        a_cursor.execute(create_table_stmt(i, the_data))

        for k in table_insert_queries(i):
            # print("CURR INS STATEMENT: " + k)
            a_cursor.execute(k)

    a_cursor.callproc('generateUnwatched')
    a_cursor.callproc('generateWatched')
    a_cursor.callproc('generateAllMovies')

    a_DB.commit()


mydb = pymysql.connect(
    host="localhost",
    user="root",
    password="yos",
    database="movieDB"
)

myCursor = mydb.cursor()

movieFile = "Movies\\Movies.html"
ingested_movie_data = evernote_2_3d_pylist(movieFile)

recreate_tables_with_data(ingested_movie_data, myCursor, mydb)

mydb.commit()

myCursor.close()
mydb.close()
