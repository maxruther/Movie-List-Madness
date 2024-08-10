import pandas as pd
from sqlalchemy import create_engine


def fill_in_metacritic():
    # Connect the SQLAlchemy engine to my local MySQL movie database
    engine = create_engine('mysql://root:yos@localhost/moviedb')
    conn = engine.connect()

    # Querying the missing Metacritic reviews from the critic_ratings table
    query = """SELECT Movie_ID, Title FROM 
    (SELECT c.Movie_ID, c.Title, c.Year, c.MetaC_Score, a.Release_Date 
    FROM critic_ratings c INNER JOIN allmovies a 
    ON c.Title=a.Title 
    WHERE c.MetaC_Score IS NULL
    ORDER BY a.Release_Date ASC) AS tt;"""

    review_df = pd.read_sql_query(query, engine, index_col='Movie_ID')
    # print(review_df)

    # # Print the film titles in the format of a python dict literal,
    # # ready for my manual data entry.
    # for i in review_df.values:
    #     print(f'"{i[0]}": ,')

    # Map for the missing reviews
    metaC_mapping = {
        # These first several films lack metacritic reviews,
        # and are unlikely to ever get them.
        # "The Ascent": ,
        # "Troll 2": ,
        # "Memories": ,
        # "Air Bud": ,
        # "Rampant": ,
        # "Inspector Ike": ,
        # "Nate - A One Man Show": ,
        "Pokemon 2000": 0.28,
        "Hundreds of Beavers": 0.82,
        "The Holdovers": 0.82,
        "The Wonderful Story of Henry Sugar": 0.85,
        "El Conde": 0.72,
        "American Fiction": 0.81,
        "Sing Sing": 0.85,
        "Outlaw Johnny Black": 0.54,
        "Saltburn": 0.61,
        "Silent Night": 0.53,
        "The Boy and the Heron": 0.91,
        "Society of the Snow": 0.72,
        "Migration": 0.56,
        "All of Us Strangers": 0.9,
        "The Teachers' Lounge": 0.82,
        "Godzilla Minus One": 0.81,
        "Upgraded": 0.59,
        "Molli and Max in the Future": 0.7,
        "Drive-Away Dolls": 0.56,
        "Love Lies Bleeding": 0.77,
        "The Beast": 0.8,
        "Civil War": 0.75,
        "Challengers": 0.82,
        "Evil Does Not Exist": 0.83,
        "Slow": 0.72,
        "Gasoline Rainbow": 0.8,
        "Babes": 0.71,
        "Furiosa: A Mad Max Saga": 0.79,
        "I Used to Be Funny": 0.74,
        "Ghostlight": 0.83,
        "Thelma": 0.77,
        "Oddity": 0.78,
        # This next film currently has too few reviews, bc it
        # only just came out (written 8/7/24).
        # "The Nature of Love": ,
    }

    # Import the critic_ratings table, as it is in the MySQL db, into a df.
    query = "SELECT * FROM critic_ratings"
    cr_df = pd.read_sql_query(query, engine, index_col='Movie_ID')
    # print(cr_df.head(5))

    # Apply the mapping to the missing reviews.
    cr_df['MetaC_Score'] = cr_df['MetaC_Score'].fillna(cr_df['Title'].map(metaC_mapping))
    # print(cr_df.head(5))

    # Load this amended table to the MySQL db, replacing the preexisting one.
    cr_df.to_sql('critic_ratings', engine, if_exists='replace', index=True)

    # Shutting down the SQL engine and db connection.
    engine.dispose()
    conn.close()
