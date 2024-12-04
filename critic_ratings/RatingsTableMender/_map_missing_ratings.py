from ._reviewer_mappings import metacritic_mapping, rt_mapping, imdb_mapping
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


def fill_missing(self, reviewer: str) -> Self:

    # Raise error if the 'critic_ratings' table has not yet been
    # imported from MySQL.
    if self.cr_df.empty:
        raise Exception("ERROR - Before running "
                        "fill_missing(), the critic_ratings table must"
                        " be fetched with get_critic_ratings_tbl().")


    valid_reviewers = ['metacritic', 
                       'rotten tomatoes', 
                       'imdb',
                       'all']

    if reviewer not in valid_reviewers:
        raise Exception("\n\nERROR: RatingsTableMender.fill_missing() - "
                        "Specified 'reviewer' is not a valid entry.\n")

    reviewer_var_dicts = {
        'imdb': {'mysql field name': 'IMDB_Score',
                 'mapping': imdb_mapping},

        'rotten tomatoes': {'mysql field name': 'RT_Score',
                 'mapping': rt_mapping},

        'metacritic': {'mysql field name': 'MetaC_Score',
                 'mapping': metacritic_mapping},
    }

    reviewer_var_set = []
    if reviewer == 'all':
        for each_reviewer in reviewer_var_dicts:
            reviewer_var_set.append(
                reviewer_var_dicts[each_reviewer]
            )
    else:
        reviewer_var_set.append(
            reviewer_var_dicts[reviewer]
        )

    for rev_vars in reviewer_var_set:
        mysql_attr = rev_vars['mysql field name']
        mapping = rev_vars['mapping']

        # Apply the mapping to the missing reviews
        self.cr_df[mysql_attr] = self.cr_df[mysql_attr].fillna(
            self.cr_df['Title'].map(mapping)
        )

        # Load this amended table to the MySQL db, replacing the
        # preexisting one.
        self.cr_df.to_sql('critic_ratings', self.engine, if_exists='replace',
                        index=True)
        
    return self
