from its_showtimes.scrapers.musicbox_scrape import musicbox_scrape
from scrapers.siskel_scrape import siskel_scrape

from schedulers.schedule_musicbox_shows import schedule_musicbox_shows
from schedulers.schedule_musicbox_shows_new_version import schedule_musicbox_shows_new_version
from schedulers.schedule_siskel_shows import schedule_siskel_shows
from schedulers.schedule_siskel_shows_new_version import schedule_siskel_shows_new_version


def scrape_and_sched():

      # Scrape the showtimes and film info      
      siskel_scrape()
      musicbox_scrape()

      # Schedule the showtimes
      # schedule_siskel_shows()
      # schedule_musicbox_shows()
      schedule_siskel_shows_new_version()
      schedule_musicbox_shows_new_version()

if __name__ == '__main__':
      scrape_and_sched()
