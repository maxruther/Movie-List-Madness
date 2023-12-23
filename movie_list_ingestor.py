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
numHeaders = len(allHeaders)

for header in allHeaders:
    if header_counter > 0:
        table_headers.append(header.text[0:-1].replace(" ", "_") + "_og")
    header_counter += 1

# Reading in all of the tables.
# At the time of writing, there are 9 tables.
data = []
table_number = 0
for table in soup.find_all("en-table"):
    # Tables are read in as 2D lists. The first array of these lists will
    # only contain the table name.
    curr_table = []
    curr_table.append([table_headers[table_number]])
    table_number += 1
    row_num = 0
    for row in table.find_all("tr"):
        curr_row = []
        dataElements = row.find_all("td")
        for element in dataElements:
            curr_elem = element.text
            liFound = element.find("li")
            if liFound:
                if liFound["data-checked"] == "true":
                    curr_elem = 1
                else:
                    curr_elem = 0
            elif curr_elem == '':
                curr_elem = "NULL"
            elif isinstance(curr_elem, str):
                if row_num > 0:
                    if "'" in curr_elem:
                        curr_elem = '"' + curr_elem + '"'
                    else:
                        curr_elem = "'" + curr_elem + "'"
                elif row_num == 0:
                    curr_elem = curr_elem.replace(" ", "_")
                    curr_elem = curr_elem.replace("Awesome?", "Rating")
            curr_row.append(curr_elem)
        curr_table.append(curr_row.copy())
        row_num += 1
    data.append(curr_table.copy())


# Clearing and deleting an existing table
def delFrmTableQry(k):
    table_name = data[k][0][0]
    delete_table_str = "DELETE FROM " + table_name
    return delete_table_str


# Dropping a table if it exists
def dropTableQry(k):
    table_name = data[k][0][0]
    drop_table_str = "DROP TABLE IF EXISTS " + table_name
    return drop_table_str


# Creating a table
def crtTableQry(k):
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

        if curr_attr == "Watched":
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
    if "Title" in table_attrs and "Director" in table_attrs:
        constraint_strings.append("PRIMARY KEY (Title, Director)")
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


def table_ins_queries(k):
    insert_stmts = []
    native_index = 1
    for i in range(2, len(data[k])):
        ins_vals_str = "INSERT INTO " + data[k][0][0] + " VALUES("
        if i < 2:
            continue
        vals = data[k][i]

        # print(data[k])
        # for val in vals:
        for l in range(len(vals)):
            val = vals[l]

            # Checking if it's a date, then replacing "/" chars if so.
            date_test_val = str(val).replace("/", "").replace("'", "")
            if "Date" in data[k][1][l] and "NULL" not in date_test_val:
            # if date_test_val.isnumeric() and len(date_test_val) > 1:
                the_date = val.replace("'", "").split("/")
                # print(the_date)
                mon = the_date[0]
                day = the_date[1]
                yr = the_date[2]
                if len(yr) < 4:
                    if int(yr) >= 50 and int(yr) <= 99:
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


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yos",
    database="movieDB"
)

myCursor = mydb.cursor()


# Recreating and loading up the various tables
for i in range(len(data)):
    myCursor.execute(dropTableQry(i))
    myCursor.execute(crtTableQry(i))

    for k in table_ins_queries(i):
        # print("CURR INS STATEMENT: " + k)
        myCursor.execute(k)

myCursor.callproc('generateUnwatched')
myCursor.callproc('generateWatched')
myCursor.callproc('generateAllMovies')

mydb.commit()

myCursor.close()
mydb.close()
