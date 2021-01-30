# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 16:54:43 2021

@author: yoliveira
"""


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait #wait elements
from selenium.webdriver.support import expected_conditions as EC #wait for iframe
import pandas as pd
import time

def getListOfNewsLinks():
    #caminho unico para as noticias utilizando css selector
    news_path = "[class *= 'NEWS']"
    links = []
    i = 0
    while len(links) < 250:
        #encontra apenas os elementos que sao noticias
        elements = driver.find_elements_by_css_selector(news_path)
        #retorna os links dos elementos utilizando list comprehension 
        links = [element.find_elements_by_tag_name("a")[0].get_attribute('href') for element in elements]
        print("Iteracao: " + str(i))
        print("Quantidade de links: " + str(len(links)))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        i += 1
        
    return links

def getNewsTitle():
    #caminho utilizando css selector para o titulo
    title_path_id = 'id_title'
    title_element = driver.find_element_by_id(title_path_id)
    return title_element.text 
    
def getNewsSubTitle():
    subTitle_path_id = 'id_deck'
    subTitle_element = driver.find_element_by_id(subTitle_path_id)
    return subTitle_element.text

def getAuthor():
    author_path = "[class = 'reviewer hcard'] > a"
    author_element = driver.find_element_by_css_selector(author_path)
    return author_element.text

def getDateNews():
    date_path = 'body > div.wrapper.articleBody > div:nth-child(1) > div.article-byline > div > span'
    date_element = driver.find_element_by_css_selector(date_path)
    return date_element.text
 
def getCountComments():
    #Rola a pagina pra baixo para que o iframe dos comentarios seja gerado
    for i in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
    
    totalFrames = driver.find_elements_by_tag_name("iframe")
    countComments_path = "[class = 'publisher-nav-color'] > [class = 'comment-count']"
        
    i = 0
    for frame in totalFrames:
        print("frame: " + str(i))
        driver.switch_to.default_content()
        try:
            driver.switch_to.frame(frame)
            countComments_element = driver.find_element_by_css_selector(countComments_path)
            countComments = countComments_element.text
            print("Encontrou o elemento no frame: " + str(i))
            driver.switch_to.default_content()
            break
        except:
            print("Elemento nao pertence a este frame")
        i += 1
        print("\n")
    
    return countComments


options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome("C:/chromedriver.exe", chrome_options = options)

driver.get('https://br.ign.com/')

driver.maximize_window()

#Pega os links das noticias da pagina 
links = getListOfNewsLinks()

'''
#Entra em cada uma das paginas para fazer a raspagem
#link = links[0]
#cria uma lista vazia que recebera uma lista de dados a cada iteração
listDataNews = []
for link in links:
    try:
        driver.get(link)
        time.sleep(2)
        
        #lista que contem os dados extraidos de uma pagina
        newsData = []
        
        #pega as informacoes do artigo
        title = getNewsTitle()
        newsData.append(title)
        
        #adiciona o SubTitulo do artigo
        subTitle = getNewsSubTitle()
        newsData.append(subTitle)
        
        #adiciona o Autor do artigo
        author = getAuthor()
        newsData.append(author)
        
        #adiciona a data do artigo
        date = getDateNews()
        newsData.append(date)
        
        #adiciona a quantidade de comentarios a lista
        nComments = getCountComments()
        newsData.append(nComments)
        
        #adiciona a URL a lista 
        newsData.append(link)
        
        listDataNews.append(newsData)
    except:
        print("Erro inesperado, pulando para a proxima noticia")
        
df_news = pd.DataFrame(listDataNews, columns = ['Title', 'SubTitle', 'Author', 'Date', 'nComments','URL'])
'''




print("Fim do programa")