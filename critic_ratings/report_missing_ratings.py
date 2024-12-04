from .RatingsTableMender import RatingsTableMender


def report_na_ratings_pre_fill(db_filepath: str) -> None:
    ratings_data_fixer = RatingsTableMender(db_filepath)

    ratings_data_fixer.connect_to_db()

    ratings_data_fixer.get_critic_ratings_tbl()

    ratings_data_fixer.join_in_ebert_ratings()

    ratings_data_fixer.report_missing_ratings('all')

    ratings_data_fixer.disconnect_from_db()
