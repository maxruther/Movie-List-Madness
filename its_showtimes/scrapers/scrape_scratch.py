from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup

import pandas as pd

from utils import create_chromedriver


driver = create_chromedriver()

driver.get('https://www.siskelfilmcenter.org/playing-this-month')


output_filename = driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/div/div/section/div/div/div[2]/div/div/table/caption').text.strip()
output_filename = output_filename.replace(' ', '')

print(output_filename)
