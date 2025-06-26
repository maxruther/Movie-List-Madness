import pandas as pd

from utils import save_output_df_to_dirs, load_latest_data


def validate_matching_columns(theater_df_list):
    first_df_columns = set(theater_df_list[0].columns)
    for i, df in enumerate(theater_df_list[1:], start=1):
        if set(df.columns) != first_df_columns:
            raise ValueError(f"Dataframe at position {i} has mismatched columns.")


def merge_theater_showtimes(*theater_dfs):
    # Confirm that the showtime datasets match in attribute set.
    validate_matching_columns(theater_dfs)
    
    # Merge showtime df's, and reset that result's index.
    merged_df = pd.concat(theater_dfs)
    merged_df = merged_df.sort_values(by=['Showtime', 'Theater']).reset_index(drop=True)
    
    # Transform the 'Showtime' attribute to a datetime field.
    merged_df['Showtime'] = pd.to_datetime(merged_df['Showtime'], utc=True, errors='raise')

    return merged_df


if __name__ == '__main__':
    sisk_df = pd.read_pickle('data/pkl/siskel/siskel_showtimes.pkl')
    mb_df = pd.read_pickle('data/pkl/musicbox/musicbox_showtimes.pkl')
    # sisk_df = pd.read_pickle('data\pkl\siskel\\test\\test_siskel_showtimes.pkl')
    # mb_df = pd.read_pickle('data/pkl/musicbox/test/test_musicbox_showtimes.pkl')
    # print(sisk_df.head())
    # print(mb_df.head())

    sisk_df = load_latest_data('siskel', 'showtimes')
    mb_df = load_latest_data('musicbox', 'showtimes')

    merge_df = merge_theater_showtimes(sisk_df, mb_df)
    # save_output_df_to_dirs(merge_df, True, 'merged_showtimes', 'merged_showtimes')
    save_output_df_to_dirs(merge_df, False, 'merged_showtimes', 'merged_showtimes')
    print(merge_theater_showtimes(sisk_df.head(), mb_df.head()))