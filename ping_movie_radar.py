from its_showtimes.scrapers.siskel_scrape import siskel_scrape
from its_showtimes.scrapers.musicbox_scrape import musicbox_scrape
from its_showtimes.schedulers.schedule_siskel_shows import schedule_siskel_shows
from its_showtimes.schedulers.schedule_musicbox_shows import schedule_musicbox_shows

from critic_ratings.scrapers.mc_search_and_scrape import mc_search_and_scrape


# siskel_showtimes_df, siskel_info_df = siskel_scrape()
# musicbox_showtimes_df, musicbox_info_df = musicbox_scrape()

movie_info_filenames = [
    'data\pkl\siskel\siskel_show_info.pkl',
    'data\pkl\musicbox\musicbox_show_info.pkl',
]

for filename in movie_info_filenames:
    mc_search_and_scrape(
        input_filepath=filename
    )

schedule_siskel_shows()
schedule_musicbox_shows()