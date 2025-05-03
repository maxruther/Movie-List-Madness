from its_showtimes.scrapers.siskel_scrape import siskel_scrape
from its_showtimes.scrapers.musicbox_scrape import musicbox_scrape

from critic_ratings.scrapers.mc_search_and_scrape import mc_search_and_scrape

from critic_ratings.db_loaders.load_mc_scrapes import load_mc_scrapes
from critic_ratings.db_loaders.load_showtimes import load_showtimes

from its_showtimes.schedulers.schedule_siskel_shows import schedule_siskel_shows
from its_showtimes.schedulers.schedule_musicbox_shows import schedule_musicbox_shows
from its_showtimes.schedulers.schedule_siskel_shows_new_version import schedule_siskel_shows_new_version
from its_showtimes.schedulers.schedule_musicbox_shows_new_version import schedule_musicbox_shows_new_version


# # Scrape the indie theater pages for showtimes and info on those
# # screened films.
# siskel_showtimes_df, siskel_info_df = siskel_scrape()
# musicbox_showtimes_df, musicbox_info_df = musicbox_scrape()

# Run the Metacritic scrape on the films pulled from the indie theater
# calendars.
movie_info_filenames = [
    'data\pkl\siskel\siskel_show_info.pkl',
    'data\pkl\musicbox\musicbox_show_info.pkl',
]

# for filename in movie_info_filenames:
#     mc_search_and_scrape(
#         input_filepath=filename
#     )

# Load the scraped film info, showtimes, and metacritic data into the
# MySQL db.
load_mc_scrapes(
    *movie_info_filenames,
    'master'
    )

load_showtimes(
    'data/pkl/siskel/siskel_showtimes.pkl',
    'data/pkl/musicbox/musicbox_showtimes.pkl',
)

# Load the theaters' showtimes to Google Calendar as events.
# schedule_siskel_shows()
# schedule_musicbox_shows()
schedule_siskel_shows_new_version()
schedule_musicbox_shows_new_version()