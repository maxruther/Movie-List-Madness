import pymysql


def drop_obsolete_og_tables(data: list[list[str | list[str | int]]],
                            cursor: pymysql.cursors.Cursor,
                            ) -> bool:
    """Drop 'og' tables in the MySQL movie db whose names don't
    correspond with any in the given data (a 3D list reflecting Evernote
     tables.)

    The presence of obsolete 'og' tables, remnant from prior runs,
    causes issues with the procedures that generate the 'AllMovies'
    tables, core to this database.

    This method requires confirmation from the user before dropping. If
    it's denied, then an exception is raised.

    Tables with '_og' suffixes each represent a table from the original
    Evernote HTML."""

    query_existing_og_tables = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = 'moviedb' and TABLE_NAME LIKE '%\\_og';"""
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
        # db, as carried out by the method 'build_core_mysql_tbls()'
        else:
            return False

    return True
