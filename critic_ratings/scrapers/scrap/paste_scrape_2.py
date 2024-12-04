from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import re


# Initialize WebDriver (Chrome)
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Chrome(options)

# Go to the website
# driver.get('https://www.metacritic.com/publication/paste-magazine/?sort-options=date')  # Replace with the URL of the website you want to scrape
driver.get('https://www.metacritic.com/movie/the-piano/critic-reviews/')
# first_paste_review_cell_xpath = '//*[@id="__layout"]/div/div[2]/div[1]/div[1]/section/div/div[contains(@class, "c-siteReview")]'
# review_cell_elements = driver.find_elements(By.XPATH, first_paste_review_cell_xpath)

# first_paste_review_cell_xpath = '//*[@id="__layout"]/div/div[2]/div[1]/div[1]/section/div[4]/div'
# review_cell_element = driver.find_element(By.XPATH, first_paste_review_cell_xpath)
problem_piano_review_xpath = '//*[@id="__layout"]/div/div[2]/div[1]/div[1]/section/div[4]/div[18]/div'
review_cell_element = driver.find_element(By.XPATH, problem_piano_review_xpath)
print(review_cell_element.text.split('\n'))

# review_cell_html_str = review_cell_element.get_attribute('innerHTML')
# soup = BeautifulSoup(review_cell_html_str, features="html.parser")

# film_title = soup.find('a', {'class': re.compile('c-siteReviewHeaderProfile_name')}).text


# print(film_title)

# for review_cell in review_cell_elements:
#     review_cell_html_string = review_cell.get_attribute('innerHTML')
#     soup = BeautifulSoup(review_cell_html_string)
    
#     print(review_cell.get_attribute('innerHTML'), '\n\n\n')

# # Wait for the page to load
# time.sleep(5) 

# # Keep scrolling until the end of the page
# last_height = driver.execute_script("return document.body.scrollHeight")

# while True:
#     # Scroll down to bottom
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

#     # Wait to load page
#     time.sleep(2)

#     # Calculate new scroll height and compare with last scroll height
#     new_height = driver.execute_script("return document.body.scrollHeight")
#     if new_height == last_height:
#         break
#     last_height = new_height

# # Now you can scrape the data from the page
# # Example: Extract all elements with the class 'item'
# items = driver.find_elements(By.CLASS_NAME, 'item')
# for item in items:
#     # Extract the data you need from each item
#     print(item.text)

# # Close the browser
driver.quit()