from typing import Self


def fill_missing_metacritic(self) -> Self:
    """Fills in some missing Metacritic scores by applying a
    mapping. (Also contains functionality to identify such missing
    scores and print out a mapping formatted for user entry.)"""

    # Read 'critic_ratings' table from MySQL db into self.cr_df ,
    # if not yet done.
    if self.cr_df.empty:
        raise Exception("ERROR - Before running "
                        "fill_missing_metacritic(), the "
                        "critic_ratings table must be fetched with"
                        "get_critic_ratings_tbl().")

    # Apply the mapping to the missing reviews.
    self.cr_df['MetaC_Score'] = self.cr_df['MetaC_Score'].fillna(
        self.cr_df['Title'].map(self.metacritic_mapping)
    )

    # Load this amended table to the MySQL db, replacing the
    # preexisting one.
    self.cr_df.to_sql('critic_ratings', self.engine,
                      if_exists='replace', index=True)

    return self


def fill_missing_rt(self) -> Self:
    """Fills in some missing RottenTomatoes scores by applying a
    mapping. (Also contains functionality to identify such missing
    scores and print out a mapping formatted for user entry.)"""

    # Read 'critic_ratings' table from MySQL db into self.cr_df ,
    # if not yet done.
    if self.cr_df.empty:
        self.get_critic_ratings_tbl()

    # Apply the mapping to the missing reviews
    self.cr_df['RT_Score'] = self.cr_df['RT_Score'].fillna(
        self.cr_df['Title'].map(self.rt_mapping)
    )

    # Load this amended table to the MySQL db, replacing the
    # preexisting one.
    self.cr_df.to_sql('critic_ratings', self.engine, if_exists='replace',
                      index=True)

    return self
