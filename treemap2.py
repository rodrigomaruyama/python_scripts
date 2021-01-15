import sys
sys.path.append('/home/maru/myenv/lib/python3.7/site-packages/')
import plotly.express as px
from selenium import webdriver
from pyvirtualdisplay import Display
from bs4 import BeautifulSoup
import datetime
import time
import requests
import os
import pandas as pd
from selenium.webdriver.common.by import By

"""
    Created by Rodrigo Maruyama in January 14th, 2021.
    This scripts creates a Treemap from the Brazil Stock market divided by its
    markets: Consumo, Industria, Basicos, Energia, Financeiro, Imobiliario e
    Utilidade Publica.
    The source is https://br.investing.com website.
"""


# Function to create a Selenium Webdriver using the chromedriver
# chromedriver link: http://chromedriver.chromium.org/

def create_driver():

    display = Display(visible=False, backend="xvfb")
    display.start()
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    browser = webdriver.Chrome('/usr/local/bin/chromedriver', options=options)
    browser.implicitly_wait(15)
    browser.set_page_load_timeout(30)
    return browser


driver = create_driver()

xpaths = ['//*[@id="17929"]', '//*[@id="17927"]', '//*[@id="17932"]',
    '//*[@id="17928"]', '//*[@id="17931"]', '//*[@id="17930"]',
    '//*[@id="17933"]']

indices = ['Consumo', 'Energia', 'Materiais basicos', 'Industrial',
    'Financeiro', 'Imobiliario', 'Utilidade publica']

url = 'https://br.investing.com/equities/brazil'
driver.get(url)

# File path to store the data we got from the source
record_file_path = 'YOUR CHOICE'

with open(record_file_path, 'w') as f:
    to_file = 'setor,nome,variacao,volume\n'
    f.write(to_file)
    for c, xpath in enumerate(xpaths):
        element = driver.find_element_by_xpath(xpath)
        element.click()
        time.sleep(3)

        tbody_xpath = '//*[@id="cross_rate_markets_stocks_1"]/tbody'
        tbody = driver.find_element(By.XPATH, tbody_xpath)

        trs = tbody.find_elements_by_tag_name('tr')
        for tr in trs:
            tds = tr.find_elements_by_tag_name('td')
            nome = tds[1].text
            variacao = tds[6].text
            variacao = variacao.replace('%','')
            variacao = variacao.replace(',','.')

            volume = tds[7].text
            volume = volume.replace(',','.')
            if 'M' in volume:
                volume = volume.replace('M','')
                volume = float(volume) * 1000000
            elif 'K' in volume:
                volume = volume.replace('K','')
                volume = float(volume) * 1000
            volume = str(volume)

            line = indices[c] + ',' + nome + ',' + variacao + ',' + volume + '\n'
            f.write(line)

driver.close()

df = pd.read_csv(record_file_path)

fig = px.treemap(df, path=['setor', 'nome'],
                 values='volume',
                 color='variacao',
                 color_continuous_scale='RdYlGn')

fig.show()
