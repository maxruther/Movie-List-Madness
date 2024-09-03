from review_remedies import *

db_path = 'mysql://root:yos@localhost/moviedb'


def fix_critic_ratings_table(db_filepath: str) -> None:
    review_data_fixer = ReviewTableMender(db_filepath)
    review_data_fixer.connect_to_db()

    review_data_fixer.fill_in_metacritic().fill_in_RT().right_join_ebert()

    review_data_fixer.disconnect_from_db()
