from selenium import webdriver

from scrapers.siskel_scrape import siskel_scrape
from scrapers.musicbox_scrape import musicbox_scrape

from schedulers.schedule_musicbox_shows import schedule_musicbox_shows
from schedulers.schedule_siskel_shows import schedule_siskel_shows


# Set up the Selenium Chromium driver
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
driver = webdriver.Chrome(options)

# Run the Siskel scrape
showtime_dict_siskel, prod_info_dict_siskel = siskel_scrape(driver)

# Run the Music Box scrape
showtime_dict_musicbox, prod_info_dict_musicbox = musicbox_scrape(driver)

# Print the dictionaries of films' showtimes and production info.
print(showtime_dict_siskel, prod_info_dict_siskel,
      sep='\n\n', end = '\n\n' + '-'*80 + '\n\n')
print(showtime_dict_musicbox, prod_info_dict_musicbox,
      sep='\n\n', end = '\n\n' + '-'*80 + '\n\n')

# Schedule the Music Box shows
schedule_siskel_shows()
schedule_musicbox_shows()

# Close the Selenium driver
driver.quit()
