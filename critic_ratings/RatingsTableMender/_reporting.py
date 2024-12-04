import pandas as pd


def report_missing_ratings(self, reviewer: str = 'all') -> None:
    """Prints reports of the films missing review scores, in the
    form of mappings-to-be, value-less dictionary literals ready for
    manual entry.

    Reviewers include 'metacritic', 'rotten tomatoes', and 'ebert'.
    The default value for the reviewer parameter, 'all', will print
    reports for all these.
    """

    valid_reviewer_entries = ['all',
                              'imdb',
                              'rotten tomatoes',
                              'metacritic',
                              'ebert']

    if reviewer not in valid_reviewer_entries:
        raise Exception("ERROR: Invalid entry for 'reviewer' in "
                        "report_missing_ratings() call.")

    reviewer_var_dicts = {
        'imdb': {'mysql field name': 'IMDB_Score',
                  'reviewer name': 'IMDb',
                  'mapping varname prefix': 'imdb'},

        'rotten tomatoes': {'mysql field name': 'RT_Score',
                            'reviewer name': 'Rotten Tomatoes',
                            'mapping varname prefix': 'rt'},

        'metacritic': {'mysql field name': 'MetaC_Score',
                       'reviewer name': 'Metacritic',
                       'mapping varname prefix': 'metacritic'},

        'ebert': {'mysql field name': 'Ebert_Score',
                  'reviewer name': 'Ebert',
                  'mapping varname prefix': 'ebert'},
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
        query = """
            SELECT Movie_ID, Title FROM (
                SELECT c.Movie_ID, c.Title, a.Release_Date
                FROM critic_ratings c INNER JOIN allmovies a
                ON c.Title=a.Title
                WHERE c.""" + rev_vars['mysql field name'] + """ IS NULL
                ORDER BY a.Release_Date ASC
                ) AS tt;
                """

        missing_reviews_df = pd.read_sql_query(query, self.engine,
                                               index_col='Movie_ID')

        # Print the film titles in the format of a python dict
        # literal, ready for my manual data entry.
        print("\n\nREPORTING MISSING "
              + rev_vars['reviewer name'].upper() +
              " RATINGS\n"
              "Value-less dictionary literal for the films missing "
              "ratings:\n")

        print(rev_vars['mapping varname prefix'] + "_mapping" +
              " = {")
        for i in missing_reviews_df.values:
            print(f'\t"{i[0]}": ,')
        print("}")