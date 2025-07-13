import pandas as pd
import os
from datetime import datetime

def load_latest_data(
        theater: str, 
        data_type: str, 
        _custom_path: str = None,
        ) -> pd.DataFrame:
    """
    Loads the most recent .pkl file for the given theater and data_type from the specified folder.

    Args:
        theater (str): Theater name, e.g., 'siskel' or 'musicbox'
        data_type (str): Data type string, e.g., 'showtimes' or 'show_info'
        folder_path (str): Directory path containing .pkl files

    Returns:
        pd.DataFrame: Loaded DataFrame from the most recent .pkl file
    """
    theater = theater.lower()
    valid_theaters = {"musicbox", "siskel"}
    if theater not in valid_theaters:
        raise ValueError(f"Invalid theater: {theater}. Expected one of {valid_theaters}")

    data_type = data_type.lower()
    folder_path = _custom_path or f'data/pkl/{theater}/single_scrapes'
    prefix = f"{theater}_{data_type}_"
    files = [
        f for f in os.listdir(folder_path)
        if f.endswith('.pkl') and f.startswith(prefix)
    ]

    if not files:
        raise FileNotFoundError(f"No .pkl files found for {theater=} and {data_type=}")

    # Extract date from filename
    def extract_date(filename):
        date_str = filename.replace(prefix, "").replace(".pkl", "")
        return datetime.strptime(date_str, "%Y-%m-%d")

    files.sort(key=extract_date, reverse=True)
    most_recent_file = os.path.join(folder_path, files[0])

    print(f"Loading latest {data_type} data for {theater}: {files[0]}")
    return pd.read_pickle(most_recent_file)