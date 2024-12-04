from typing import List

import pymysql


def build_omdb_tbl(cursor: pymysql.cursors.Cursor,
                   omdb_data: List[List[int | str | float]]
                   ) -> None:
    """Creates the 'omdb' table (from square one) using the
    abbreviated/reduced OMDB data prepared by the
    prep_omdb() method."""

    # Drop the existing 'omdb' table in the MySQL db.
    cursor.execute("DROP TABLE IF EXISTS omdb")

    # Construct the 'CREATE TABLE' SQL statement.
    create_table_str = "CREATE TABLE IF NOT EXISTS omdb("

    col_names = ['Movie_ID', 'Title', 'Year', 'OMDB_Release', 'Runtime',
                 'Genres', 'Directors', 'Writers', 'Actors',
                 'IMDB_Score', 'RT_Score', 'MetaC_Score', 'Earnings']
    num_cols = len(col_names)

    for i in range(num_cols):
        curr_attr = col_names[i]
        var_type = " varchar(80)"

        if curr_attr in ['Movie_ID', 'Runtime', 'Earnings']:
            var_type = ' int'

        if "Score" in curr_attr:
            var_type = " float"

        create_table_str += curr_attr + var_type + ', '
    create_table_str += ' PRIMARY KEY(Movie_ID))'

    # Execute the 'CREATE TABLE' statement.
    cursor.execute(create_table_str)

    # Create and execute the 'INSERT' statements.
    arg_string = '(' + ", ".join(['%s'] * num_cols) + ')'
    cursor.executemany("INSERT INTO omdb VALUES " + arg_string,
                       omdb_data)


def build_genre_tbl(cursor: pymysql.cursors.Cursor,
                    prepped_data: List[List[int | str]]
                    ) -> None:
    """Creates the 'genres' table (from square one) using the
    genre data and list prepared by the prep_genre() method."""

    # Drop the existing genre table in the MySQL db.
    cursor.execute("DROP TABLE IF EXISTS genres")

    # Construct the 'CREATE TABLE' SQL statement
    create_table_str = "CREATE TABLE IF NOT EXISTS genres("

    col_names = prepped_data.pop(0)

    num_cols = len(col_names)
    for i in range(num_cols):
        curr_attr = col_names[i].replace("-", "")
        var_type = " varchar(80)"

        if curr_attr not in ['Title', 'Year']:
            var_type = " int"

        create_table_str += curr_attr + var_type + ', '

    # Adding constraints as necessary
    constraint_strings = []
    # if "Movie_ID" in col_names:
    #     constraint_strings.append("PRIMARY KEY (Movie_ID)")
    if "Movie_ID" in col_names:
        constraint_strings.append("FOREIGN KEY(Movie_ID) REFERENCES "
                                  "allmovies(Movie_ID)")
    for attr in col_names:
        attr = attr.replace("-", "")
        if attr not in ["Movie_ID", "Title", "Year"]:
            constraint_strings.append("CHECK (" + attr + " in (0, 1))")

    if len(constraint_strings) > 0:
        total_constraint_str = ", ".join(constraint_strings)
        total_constraint_str = total_constraint_str + ")"
        create_table_str = create_table_str + total_constraint_str

    # Execute the 'CREATE TABLE' statement
    cursor.execute(create_table_str)

    # Create and execute the 'INSERT' statements
    value_rpl_str = "(" + ", ".join(["%s"] * num_cols) + ")"
    cursor.executemany("INSERT INTO genres VALUES " +
                       value_rpl_str,
                       prepped_data)


def build_ratings_tbl(cursor: pymysql.cursors.Cursor,
                      ratings_data: List[List[int | str
                                                      | float]]
                      ) -> None:
    """Creates the 'critic_ratings' table (from square one) using the
    ratings data prepared by the prep_ratings() method."""

    # Drop the existing critic_ratings table in the MySQL db.
    cursor.execute("DROP TABLE IF EXISTS critic_ratings")

    # Construct the 'CREATE TABLE' SQL statement
    create_table_str = "CREATE TABLE IF NOT EXISTS critic_ratings("
    ratings_data_col_names = ['Movie_ID', 'Title', 'Year', 'IMDB_Score',
                              'RT_Score', 'MetaC_Score']
    num_cols = len(ratings_data_col_names)
    for i in range(num_cols):
        curr_attr = ratings_data_col_names[i]
        var_type = " varchar(80)"

        if "Score" in curr_attr:
            var_type = " float"
        elif "Movie_ID" in curr_attr:
            var_type = " int NOT NULL"

        create_table_str += curr_attr + var_type + ', '
    create_table_str += 'FOREIGN KEY(Movie_ID) REFERENCES ' \
                        'allmovies(Movie_ID))'
    # create_table_str += 'PRIMARY KEY(Movie_ID) )'
    # print(create_table_str)

    # Execute the 'CREATE TABLE' statement
    cursor.execute(create_table_str)

    # Insert the movie ratings records into this new critic_ratings
    # table.
    cursor.executemany("INSERT INTO critic_ratings VALUES (%s, %s, %s,"
                       " %s, %s, %s)", ratings_data)
