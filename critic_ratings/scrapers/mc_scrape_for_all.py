from mc_search_and_scrape import mc_search_and_scrape
import time

filmlist_filepaths = [
    'data/pkl/ebert/ebert_recent_reviews.pkl',
    'data/pkl/musicbox/musicbox_show_info.pkl',
    'data/pkl/siskel/siskel_inferior_show_info.pkl',
    'data/pkl/my_watched_films/my_watched_films.pkl',
]

start_time = time.time()

for filepath in filmlist_filepaths:
    # Get the filename without the extension
    filename = filepath.split('/')[-1].split('.')[0]
    print(f"Scraping for file: {filename}",
          f"( full path: {filepath})",
          sep='\n')

    # Call the mc_search_and_scrape function with the constructed paths
    mc_search_and_scrape(filepath)