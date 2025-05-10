import pandas as pd


def reconcile_multiple_film_results(
        film_title: str,
        film_year: str,
        film_director: str,
        mc_scrape_df: pd.DataFrame,
        ) -> dict:
    """
    This function reconciles multiple film results from the Metacritic scrape.
    It returns a dictionary with the best match for the given title, year, and director.
    """
    # Filter the DataFrame for the given title and year
    filtered_df = mc_scrape_df[
        (mc_scrape_df['Title Searched'] == film_title) &
        (mc_scrape_df['Year Searched'] == film_year) &
        (mc_scrape_df['Director Searched'] == film_director)
    ]

    # If there are no results, return an empty dictionary
    if filtered_df.empty:
        return {}

    # Check if there are multiple results
    if len(filtered_df) > 1:
        # Filter for the best match based on director
        filtered_df = filtered_df[filtered_df['Director Result'] == film_director]

    # Return the first result as a dictionary
    return filtered_df.iloc[0].to_dict(orient='records')[0]