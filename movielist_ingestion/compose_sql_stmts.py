def create_table_stmt(k: int,
                      data: list[list[str | list[str | int]]],
                      ) -> str:
    """Returns a "CREATE TABLE IF NOT EXISTS" statement for the MySQL db,
    given the read-in Evernote data and the table's index therein.

    ERROR NOTE: If any Evernote tables bore an unnamed column, it will
    trigger an error in this method."""
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
