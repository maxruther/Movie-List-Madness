import pandas as pd
from sqlalchemy import create_engine


def fill_in_RT():
    # Connect the SQLAlchemy engine to my local MySQL movie database
    engine = create_engine('mysql://root:yos@localhost/moviedb')
    conn = engine.connect()

    # Query the missing RT reviews from the critic_ratings table
    query = """SELECT Movie_ID, Title FROM
    (SELECT c.Movie_ID, c.Title, c.Year, c.RT_Score, a.Release_Date 
    FROM critic_ratings c INNER JOIN allmovies a ON c.Title=a.Title
    WHERE c.RT_Score IS NULL
    ORDER BY a.Release_Date ASC) AS tt;"""

    missing_RT_df = pd.read_sql_query(query, engine, index_col='Movie_ID')
    # print(missing_RT_df)

    # # Print the film titles in the format of a python dict literal,
    # # ready for my manual data entry.
    # for i in missing_RT_df.values:
    #     print(f'"{i[0]}": ,')

    # Creating the mapping for the missing reviews
    RT_mapping = {
        # The following commented out film indeed lacks RT (critical) scores.
        # "Memories": ,
        "Pokemon 2000": 0.19,
        "Possessor": 0.94,
        "The Card Counter": 0.87,
        "TÃ¡r": 0.91,
        "Suzume": 0.96,
        "Talk to Me": 0.94,
    }

    # Import the critic_ratings table, as it is in the MySQL db, into a df.
    query = "SELECT * FROM critic_ratings"
    cr_df = pd.read_sql_query(query, engine, index_col='Movie_ID')
    # print(cr_df.head(5))

    # Printing the records with missing 'RT_Score'
    missing_RT_mask = cr_df['RT_Score'].isnull()
    print(cr_df[missing_RT_mask])

    # Apply the mapping to the missing reviews
    cr_df['RT_Score'] = cr_df['RT_Score'].fillna(cr_df['Title'].map(RT_mapping))
    print(cr_df[missing_RT_mask])

    # Load this amended table to the MySQL db, replacing the preexisting one.
    cr_df.to_sql('critic_ratings', engine, if_exists='replace', index=True)

    # Shutting down the SQL engine and db connection.
    engine.dispose()
    conn.close()