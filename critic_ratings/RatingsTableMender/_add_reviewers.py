import pandas as pd


def join_in_ebert_ratings(self,
                          ebert_filepath: str = None,
                          ):
    """Read in the ebert_ratings.csv and right-join it to the
    critics_ratings table."""

    if not self.isConnected:
        raise Exception("ERROR - ReviewTableMender - You cannot"
                        "get the critic ratings table before first"
                        "connecting to the db (via connect_to_db() "
                        "method called with valid db path.)")

    # Read 'critic_ratings' table from MySQL db into self.cr_df ,
    # if not yet done.
    if self.cr_df.empty:
        self.get_critic_ratings_tbl()

    # Read in the Ebert ratings from file
    if ebert_filepath:
        ebert_df = pd.read_csv(ebert_filepath,
                               index_col='Movie_ID')
    else:
        ebert_df = pd.read_csv(
            'data/csv/ebert/ratings_manually_gathered/ebert_ratings.csv',
            index_col='Movie_ID'
            )

    # Change 'Year' attribute's type to string (from int).
    ebert_df['Year'] = ebert_df['Year'].astype(str)

    # Join the Ebert ratings onto the critic_ratings df
    cr_plus_ebert_df = self.cr_df.merge(ebert_df, how='left',
                                        on=['Title', 'Year'])
    cr_plus_ebert_df.index = range(1, len(cr_plus_ebert_df) + 1)
    cr_plus_ebert_df.index.names = ['Movie_ID']

    # Load this amended table to the MySQL db, replacing the
    # preexisting one.
    cr_plus_ebert_df.to_sql('critic_ratings', self.engine,
                            if_exists='replace', index=True)

    return self
