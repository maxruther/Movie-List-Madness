import pandas as pd
from sqlalchemy import create_engine


class RatingsTableMender:
    """Puts the finishing touches on the critic_ratings table
    by 1) filling in missing Metacritic and Rotten Tomatoes
    reviews and 2) adding the Ebert ratings (from file.)"""

    def __init__(self, db_path: str) -> None:
        self.isConnected = False
        self.conn = None
        self.engine = None
        self.db_path = db_path

        self.cr_df: pandas.DataFrame = pd.DataFrame()

    # Import the various film review mappings, which are used by the
    # 'fill_missing' methods defined in the map_missing_ratings module.
    from ._reviewer_mappings import metacritic_mapping, rt_mapping

    # Import this class's various functions from the separate modules.
    from ._map_missing_ratings import fill_missing_metacritic, fill_missing_rt
    from ._add_reviewers import join_in_ebert_ratings
    from ._reporting import report_missing_ratings

    def set_db_path(self, db_path: str) -> None:
        self.db_path = db_path

    def connect_to_db(self) -> None:
        self.engine = create_engine('mysql://root:yos@localhost/moviedb')
        self.conn = self.engine.connect()
        self.isConnected = True

    def disconnect_from_db(self) -> None:
        self.engine.dispose()
        self.conn.close()
        self.isConnected = False

    def get_critic_ratings_tbl(self):
        if not self.isConnected:
            raise Exception("ERROR - ReviewTableMender - You cannot"
                            "get the critic ratings table before first"
                            "connecting to the db (via connect_to_db() "
                            "method called with valid db path.)")

        query = "SELECT * FROM critic_ratings"
        self.cr_df = pd.read_sql_query(query, self.engine,
                                       index_col='Movie_ID')
