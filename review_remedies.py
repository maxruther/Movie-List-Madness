import pandas as pd
from sqlalchemy import create_engine

class remedyReviewTable:
    """Puts the finishing touches on the critic_ratings table
    by 1) filling in missing Metacritic and Rotten Tomatoes
    reviews and 2) adding the Ebert ratings (from file.)"""
    def __init__(self, db_path):
        self.db_path = db_path
    
    def connect_to_db(self):
        self.engine = create_engine('mysql://root:yos@localhost/moviedb')
        self.conn = self.engine.connect()

    def disconnect_from_db(self):
        self.engine.dispose()
        self.conn.close()

    def fill_in_metacritic(self):
        # Querying the missing Metacritic reviews from the critic_ratings table
        query = """SELECT Movie_ID, Title FROM 
        (SELECT c.Movie_ID, c.Title, c.Year, c.MetaC_Score, a.Release_Date 
        FROM critic_ratings c INNER JOIN allmovies a 
        ON c.Title=a.Title 
        WHERE c.MetaC_Score IS NULL
        ORDER BY a.Release_Date ASC) AS tt;"""

        review_df = pd.read_sql_query(query, self.engine, index_col='Movie_ID')
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
        cr_df = pd.read_sql_query(query, self.engine, index_col='Movie_ID')
        # print(cr_df.head(5))

        # Apply the mapping to the missing reviews.
        cr_df['MetaC_Score'] = cr_df['MetaC_Score'].fillna(cr_df['Title'].map(metaC_mapping))
        # print(cr_df.head(5))

        # Load this amended table to the MySQL db, replacing the preexisting one.
        cr_df.to_sql('critic_ratings', self.engine, if_exists='replace', index=True)

        return self

    def fill_in_RT(self):
        # Query the missing RT reviews from the critic_ratings table
        query = """SELECT Movie_ID, Title FROM
        (SELECT c.Movie_ID, c.Title, c.Year, c.RT_Score, a.Release_Date 
        FROM critic_ratings c INNER JOIN allmovies a ON c.Title=a.Title
        WHERE c.RT_Score IS NULL
        ORDER BY a.Release_Date ASC) AS tt;"""

        missing_RT_df = pd.read_sql_query(query, self.engine, index_col='Movie_ID')
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
        cr_df = pd.read_sql_query(query, self.engine, index_col='Movie_ID')
        # print(cr_df.head(5))

        # # Printing the records with missing 'RT_Score'
        # missing_RT_mask = cr_df['RT_Score'].isnull()
        # print(cr_df[missing_RT_mask])

        # Apply the mapping to the missing reviews
        cr_df['RT_Score'] = cr_df['RT_Score'].fillna(cr_df['Title'].map(RT_mapping))
        # print(cr_df[missing_RT_mask])

        # Load this amended table to the MySQL db, replacing the preexisting one.
        cr_df.to_sql('critic_ratings', self.engine, if_exists='replace', index=True)

        return self
    
    def right_join_ebert(self):
        # Connect the SQLAlchemy engine to my local MySQL movie database
        self.engine = create_engine('mysql://root:yos@localhost/moviedb')
        conn = self.engine.connect()

        # Import the critic_ratings table, as it is in the MySQL db, into a df.
        query = "SELECT * FROM critic_ratings"
        cr_df = pd.read_sql_query(query, self.engine, index_col='Movie_ID')
        # print(cr_df.head(5))

        # Read in the Ebert ratings from file
        ebert_df = pd.read_csv('ebert_ratings.csv', index_col='Movie_ID')
        ebert_df['Year'] = ebert_df['Year'].astype(str)
        # print(ebert_df.head(5))

        # Join the Ebert ratings onto the critic_ratings df
        cr_plus_ebert_df = cr_df.merge(ebert_df, how='left', on=['Title','Year'])
        cr_plus_ebert_df.index = range(1, len(cr_plus_ebert_df)+1)
        cr_plus_ebert_df.index.names = ['Movie_ID']
        # print(cr_plus_ebert_df.head(5))

        # Load this amended table to the MySQL db, replacing the preexisting one.
        cr_plus_ebert_df.to_sql('critic_ratings', self.engine, if_exists='replace',
                                index=True)
        
        return self
