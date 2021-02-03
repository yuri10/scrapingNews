# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 22:58:03 2021

@author: yoliveira
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait #wait elements
from selenium.webdriver.support import expected_conditions as EC #wait for iframe
import pandas as pd
import time
import re #regex para limpeza dos dados
import unidecode
from datetime import datetime #pegar dia e hora em que houve a extração


def GetNewsTitle():
    titulo_elemento = driver.find_element_by_css_selector('#news-title-image-div-15127 > div > div.hide-on-small-only > h1')
    return titulo_elemento.text
    
def GetNewsSubtitle():
    subtitulo_elemento = driver.find_element_by_css_selector('#news_content_15127 > div.news-content-header > div.time-line > div.sMessage > em')
    return subtitulo_elemento.text

def GetNewsAuthor():
    autor_elemento = driver.find_element_by_css_selector('#news_content_15127 > div.news-content-header > div.time-line > div:nth-child(2) > a')
    return autor_elemento.text

def GetNewsdate():
    data_elemento = driver.find_element_by_css_selector('#time_1')
    return data_elemento.get_attribute('datetime')


options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
driver = webdriver.Chrome("C:/chromedriver.exe", chrome_options = options)

driver.get('https://www.gamevicio.com/games/')

driver.maximize_window()

actions = ActionChains(driver)

actions.move_to_element(btnLoadMorePages_element).perform()


