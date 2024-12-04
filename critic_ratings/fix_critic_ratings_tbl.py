from .RatingsTableMender import RatingsTableMender


def fix_critic_ratings_tbl(db_filepath: str,
                           na_report: bool = False) -> None:
    ratings_data_fixer = RatingsTableMender(db_filepath)

    ratings_data_fixer.connect_to_db()

    ratings_data_fixer.get_critic_ratings_tbl()

    ratings_data_fixer.fill_missing('metacritic')
    ratings_data_fixer.fill_missing('rotten tomatoes')
    ratings_data_fixer.fill_missing('imdb')

    ratings_data_fixer.join_in_ebert_ratings()

    if na_report:
        ratings_data_fixer.report_missing_ratings('all')

    ratings_data_fixer.disconnect_from_db()
