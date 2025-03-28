from scrapers.musicbox_scrape import musicbox_scrape
from scrapers.siskel_showtime_scrape import siskel_showtime_scrape
from scrapers.siskel_info_scrape import siskel_info_scrape

from schedulers.schedule_musicbox_shows import schedule_musicbox_shows
from schedulers.schedule_siskel_shows import schedule_siskel_shows


def scrape_and_sched(
          preview_output=False,
):
    
    # Run the Siskel scrape
#     siskel_showtime_dict, siskel_info_df = siskel_showtime_scrape()
      siskel_showtime_dict, siskel_show_info_df_inferior = siskel_showtime_scrape()
      siskel_show_info_df = siskel_info_scrape()

      if preview_output:
            # Showtimes
            for movie, showtime_list in list(siskel_showtime_dict.items())[:5]:
                  print(movie)
                  for showtime in showtime_list:
                        print(f'\t{showtime}')
                  print()

            # A separator
            print('\n' + '-'*80 + '\n')

            # Inferior show info
            print(siskel_show_info_df_inferior.head(), '\n')

            # Another separator
            print('\n' + '-'*80 + '\n')

            # Superior show info
            print(siskel_show_info_df.head(), '\n')
      

      # Run the Music Box scrape
      musicbox_showtime_dict, musicbox_info_df = musicbox_scrape()

      if preview_output:
            # Showtimes
            for movie, showtime_list in list(musicbox_showtime_dict.items())[:5]:
                  print(movie)
                  for showtime in showtime_list:
                        print(f'\t{showtime}')
                  print()
            
            # A separator
            print('\n' + '-'*80 + '\n')

            # Show info
            print(musicbox_info_df.head(), '\n')


      # Schedule the Music Box shows
      schedule_siskel_shows()
      schedule_musicbox_shows()


if __name__ == '__main__':
      scrape_and_sched()
      # scrape_and_sched(preview_output=True)
