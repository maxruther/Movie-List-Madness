import os
from datetime import datetime

from its_showtimes.scrapers.siskel_scrape import siskel_scrape
from its_showtimes.scrapers.musicbox_scrape import musicbox_scrape

from critic_ratings.scrapers.mc_search_and_scrape import mc_search_and_scrape

from critic_ratings.db_loaders.load_mc_scrapes import load_mc_scrapes
from critic_ratings.db_loaders.load_showtimes import load_showtimes

from its_showtimes.schedulers.schedule_siskel_shows import schedule_siskel_shows
from its_showtimes.schedulers.schedule_musicbox_shows import schedule_musicbox_shows
from its_showtimes.schedulers.schedule_siskel_shows_new_version import schedule_siskel_shows_new_version
from its_showtimes.schedulers.schedule_musicbox_shows_new_version import schedule_musicbox_shows_new_version

## SHOWTIME SCRAPE

# Scrape the indie theater pages for showtimes and info on those
# screened films.
siskel_showtimes_df, siskel_info_df = siskel_scrape()
musicbox_showtimes_df, musicbox_info_df = musicbox_scrape()


## METACRITIC SCRAPE

movie_info_filenames = []
valid_theaters = {"musicbox", "siskel"}

for theater in valid_theaters:
    folder_path = f'data/pkl/{theater}/single_scrapes'
    prefix = f'{theater}_show_info_'
    
    files = [
        f for f in os.listdir(folder_path)
        if f.endswith('.pkl') and f.startswith(prefix)
    ]
    if not files:
        raise FileNotFoundError(f"No .pkl files found for {theater=} and 'show_info'.")
    
    def extract_date(filename):
        date_str = filename.replace(prefix, "").replace(".pkl", "")
        return datetime.strptime(date_str, "%Y-%m-%d")

    files.sort(key=extract_date, reverse=True)
    most_recent_file = os.path.join(folder_path, files[0])

    movie_info_filenames.append(most_recent_file)

# Run the Metacritic scrape on the films pulled from the indie theater
# calendars.

# # movie_info_filenames = [
# #     'data\pkl\siskel\single_scrapes\siskel_show_info_2025-07-16.pkl',
# #     'data\pkl\musicbox\musicbox_show_info.pkl',
# # ]
for filename in movie_info_filenames:
    mc_search_and_scrape(
        input_filepath=filename
    )

# LOAD SCRAPED DATA INTO DB
# Load the scraped film info, showtimes, and metacritic data into the
# MySQL db.
load_mc_scrapes(
    *movie_info_filenames,
    'master'
    )

# load_showtimes(
#     'data/pkl/siskel/siskel_showtimes.pkl',
#     'data/pkl/musicbox/musicbox_showtimes.pkl',
# )
load_showtimes()

# # Load the theaters' showtimes to Google Calendar as events.
# # schedule_siskel_shows()
# # schedule_musicbox_shows()
# schedule_siskel_shows_new_version()
# schedule_musicbox_shows_new_version()