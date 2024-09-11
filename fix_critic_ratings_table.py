from critic_ratings import RatingsTableMender


def fix_critic_ratings_table(db_filepath: str) -> None:
    ratings_data_fixer = RatingsTableMender(db_filepath)

    ratings_data_fixer.connect_to_db()

    ratings_data_fixer.get_critic_ratings_tbl()

    ratings_data_fixer.fill_missing_metacritic().fill_missing_rt().join_in_ebert_ratings()

    # ratings_data_fixer.report_missing_ratings('all')

    ratings_data_fixer.disconnect_from_db()
