import pandas as pd

from datetime import date, timedelta


def get_first_n_days_of_showtime_df(
        df = pd.DataFrame,
        n_days: int = 5,
        first_show_date: date = None,
        ) -> pd.DataFrame:
    """
    Get the first n days of showtimes from the given DataFrame.
    If first_show_date is not provided, it will be set to the minimum date in the DataFrame.
    """
    
    if not first_show_date:
        first_show_date = df['Showtime'].min().date()
    
    n_days_after_show_date = first_show_date + timedelta(days=n_days-1)

    first_n_days_of_shows_df = df[
        (df['Showtime_Date'] >= first_show_date) &
        (df['Showtime_Date'] <= n_days_after_show_date)
        ]
    
    return first_n_days_of_shows_df.reset_index(drop=True)