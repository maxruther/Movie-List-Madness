import pandas as pd
from sqlalchemy import create_engine

def right_join_ebert():
    # Connect the SQLAlchemy engine to my local MySQL movie database
    engine = create_engine('mysql://root:yos@localhost/moviedb')
    conn = engine.connect()

    # Import the critic_ratings table, as it is in the MySQL db, into a df.
    query = "SELECT * FROM critic_ratings"
    cr_df = pd.read_sql_query(query, engine, index_col='Movie_ID')
    print(cr_df.head(5))

    # Read in the Ebert ratings from file
    ebert_df = pd.read_csv('ebert_ratings.csv', index_col='Movie_ID')
    ebert_df['Year'] = ebert_df['Year'].astype(str)
    print(ebert_df.head(5))

    # Join the Ebert ratings onto the critic_ratings df
    cr_plus_ebert_df = cr_df.merge(ebert_df, how='left', on=['Title','Year'])
    cr_plus_ebert_df.index = range(1, len(cr_plus_ebert_df)+1)
    cr_plus_ebert_df.index.names = ['Movie_ID']
    print(cr_plus_ebert_df.head(5))

    # Load this amended table to the MySQL db, replacing the preexisting one.
    cr_plus_ebert_df.to_sql('critic_ratings', engine, if_exists='replace',
                            index=True)

    # Shutting down the SQL engine and db connection.
    engine.dispose()
    conn.close()