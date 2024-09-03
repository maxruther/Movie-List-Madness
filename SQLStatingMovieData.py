import pymysql.connections


def drop_table_stmt(k: int,
                    data: list[list[str | list[str | int]]],
                    ) -> str:
    """Returns a "DROP TABLE IF EXISTS" statement for the MySQL db, given
    the read-in Evernote data and the table's index therein."""
    table_name = data[k][0][0]
    drop_table_str = "DROP TABLE IF EXISTS " + table_name
    # print(drop_table_str)
    return drop_table_str


def create_table_stmt(k: int,
                      data: list[list[str | list[str | int]]],
                      ) -> str:
    """Returns a "CREATE TABLE IF NOT EXISTS" statement for the MySQL db,
    given the read-in Evernote data and the table's index therein."""
    table_name = data[k][0][0]

    # Create list of attributes from the Evernote table header.
    table_attrs = []
    for attr in data[k][1]:
        table_attrs.append(attr)

    attr_count = len(table_attrs)
    create_table_str = "CREATE TABLE IF NOT EXISTS " + table_name + "("

    # Collecting the tables attributes into a list of strings
    attr_declarations = []
    for i in range(attr_count):
        curr_attr = table_attrs[i]
        attr_type = " varchar(80)"

        if curr_attr in ["Watched", "Movie_ID"]:
            attr_type = " int"
        elif "Date" in curr_attr:
            attr_type = " date"

        attr_declarations.append(curr_attr + attr_type + ", ")

    attr_declarations.append("native_ordering int NOT NULL UNIQUE)")

    # Construct the "CREATE TABLE" statement, though it lacks constraints.
    for i in attr_declarations:
        create_table_str += i

    # Adding table-specific constraints (in SQL)
    constraint_strings = []

    # Make 'Movie_ID' a primary key.
    if "Movie_ID" in table_attrs:
        constraint_strings.append("PRIMARY KEY (Movie_ID)")

    # Make 'Watched' and 'Watched_in_theater' binary by constraining
    # them to 0 and 1.
    if "Watched" in table_attrs:
        constraint_strings.append("CHECK (Watched in (0, 1))")
    if "Watched_in_theater" in table_attrs:
        constraint_strings.append("CHECK (Watched_in_theater in (0, 1))")

    # When multiple constraints apply, handle statement's formatting
    if len(constraint_strings) > 0:
        total_constraint_str = ", ".join(constraint_strings)
        total_constraint_str = total_constraint_str + ")"
        create_table_str = create_table_str[:-1] + ", " + total_constraint_str

    # print(create_table_str)
    return create_table_str


def table_insert_stmts(k: int,
                       data: list[list[str | list[str | int]]],
                       ) -> list[str]:
    """Returns a list of SQL 'INSERT' statements for each entry of an
    Evernote table, given the read-in Evernote data and the table's
    index therein."""
    insert_stmts = []

    # An attribute 'Native Ordering' will track the entries' original
    # ordering within the Evernote table. native_index populates this.
    native_index = 1

    table = data[k]
    # Iterate through the table's entries (skipping its name and header)
    for i in range(2, len(table)):
        ins_vals_str = "INSERT INTO " + table[0][0] + " VALUES("

        vals = table[i]
        for l in range(len(vals)):
            val = vals[l]

            # Handling date values
            date_test_val = str(val).replace("/", "").replace("'", "")
            if "Date" in table[1][l] and "NULL" not in date_test_val:
                the_date = val.replace("'", "").split("/")

                # Parse the date
                mon = the_date[0]
                day = the_date[1]
                yr = the_date[2]

                # Infer century, when it isn't provided.
                if len(yr) < 4:
                    if 50 <= int(yr) <= 99:
                        yr = "19" + yr
                    else:
                        yr = "20" + yr
                val = "'" + yr + "-" + mon + "-" + day + "'"

            # If there are more values to process, add a separator of
            # ', ' to the SQL-Insert string.
            if l < len(vals) - 1:
                ins_vals_str += str(val) + ", "
            # Add 'native index/ordering' to the end of the record.
            else:
                ins_vals_str += str(val) + ", " + str(native_index) + ")"
                native_index += 1
        insert_stmts.append(ins_vals_str)

    # print(insert_stmts)
    return insert_stmts


def drop_old_og_tables(data: list[list[str | list[str | int]]],
                       cursor: pymysql.cursors.Cursor,
                       ) -> bool:
    """Query movie db for tables that end in '_og'. This is my naming
    convention for tables that represent each Evernote table."""

    query_existing_og_tables = 'SELECT TABLE_NAME ' \
                               'FROM INFORMATION_SCHEMA.TABLES ' \
                               'WHERE TABLE_SCHEMA = "moviedb"  ' \
                               'and TABLE_NAME LIKE "%\\_og";'
    cursor.execute(query_existing_og_tables)

    # Creating a list of the names of the existing MySQL tables that
    # end in '_og'.
    existing_SQL_og_tables = []
    existing_og_tables = cursor.fetchall()
    for i in existing_og_tables:
        existing_SQL_og_tables.append(i[0])

    # Creating a list of all table names from the Evernote data.
    table_names = []
    for i in data:
        table_names.append(i[0][0].lower())

    # Creating a list of all '_og' tables that don't match an Evernote
    # table.
    og_table_not_in_data = []
    for i in existing_SQL_og_tables:
        if i not in table_names:
            og_table_not_in_data.append(i)

    # Drop extraneous '_og' tables
    if og_table_not_in_data:
        print('\nWARNING: Tables exist in the MySQL database that '
              'don\'t resemble any from this submitted data:')
        for i in og_table_not_in_data:
            print(i)

        # Get user permission to delete extraneous '_og' tables
        user_response = input('\nProceed with deleting (Y) or don\'t, '
                              'and cancel this update to the MySQL db'
                              ' (N).').lower()
        while user_response not in ['y', 'n']:
            user_response = input("\nINVALID INPUT\nEnter (Y) or (N) to"
                                  " indicate whether said tables should"
                                  " be deleted, as a necessary part of"
                                  " this processing.").lower()

        # If given permission, delete the tables.
        if user_response == 'y':
            for table in og_table_not_in_data:
                cursor.execute("DROP TABLE IF EXISTS " + table)
            return True
        # If permission denied, return False to end updating of MySQL
        # db, as carried out by the method 'recreate_tables_with_data()'
        else:
            return False

    return True


def recreate_tables_with_data(data: list[list[str | list[str | int]]], db: pymysql.connections.Connection) -> None:
    """In the MySQL db, creates all movie tables from scratch, from the
    Evernote file.
    NOTE: Existing MySQL tables are DELETED & RECREATED if they share
    a name with an Evernote table. This is not a process that appends
    or updates existing MySQL tables."""

    # Create cursor from the db connection
    cursor = db.cursor()

    # This process drops all existing tables before recreating them. In
    # order to do so, the OMDB-related tables must be dropped first, as
    # they are child relations to the 'allmovies' table.
    omdb_tables = ['omdb', 'genres', 'critic_ratings']
    for table in omdb_tables:
        cursor.execute("DROP TABLE IF EXISTS " + table)

    if not drop_old_og_tables(data, cursor):
        print("\nCANCELLING UPDATE OF MySQL DATABASE, PER USER"
              " REQUEST\n")
        return

    # Every table in the Evernote data, as processed from file by
    # 'evernote_2_3d_pylist()', is created from scratch.
    table_count = len(data)
    for i in range(table_count):
        # Delete the existing table in MySQL if it shares this Evernote
        # table's name.
        cursor.execute(drop_table_stmt(i, data))

        # Create a table in MySQL for this Evernote table.
        #
        # ERROR NOTE: If an Evernote table has unnamed columns, errors
        # will here arise.
        # print(create_table_stmt(i, data))
        cursor.execute(create_table_stmt(i, data))

        # Insert a row for each of this table's movie records.
        for k in table_insert_stmts(i, data):
            # print("CURR INS STATEMENT: " + k)
            cursor.execute(k)

    # Once all the tables are read in, a few more MySQL tables are
    # generated by SQL procedures that I've defined in advance.

    # Create table 'allunwatched', containing all movies that I've yet
    # to watch.
    cursor.callproc('generateUnwatched')

    # Create table 'allwatched', containing all the listed movies that I
    # have watched.
    cursor.callproc('generateWatched')

    # Create table 'allmovies', which simply contains all movie records,
    # regardless of whether they're of ones I've yet watched.
    cursor.callproc('generateAllMovies')

    db.commit()
