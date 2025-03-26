from siskel_showtime_scrape import siskel_showtime_scrape
from siskel_info_scrape import siskel_info_scrape

showtime_dict, show_info_df_inferior = siskel_showtime_scrape()
show_info_df = siskel_info_scrape()


# # Print previews of the scraped output:

# Showtimes
for movie, showtime_list in list(showtime_dict.items())[:5]:
    print(movie)
    for showtime in showtime_list:
        print(f'\t{showtime}')
    print()

# A separator
print('\n' + '-'*80 + '\n')

# Inferior show info
print(show_info_df_inferior.head(), '\n')

# Another separator
print('\n' + '-'*80 + '\n')

# Superior show info
print(show_info_df.head(), '\n')