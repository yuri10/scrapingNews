# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 20:19:16 2021

@author: yoliveira
"""

from selenium.webdriver.support.ui import WebDriverWait #wait elements
from selenium.webdriver.support import expected_conditions as EC #wait for iframe
import pandas as pd
import time
import re #regex para limpeza dos dados
import unidecode
import sys

from datetime import datetime #pegar dia e hora em que houve a extração
from selenium.webdriver.common.action_chains import ActionChains

def getListOfNewsLinksAdrenaline(driver):
    #caminho unico para as noticias utilizando css selector
    news_path = "article.post-h > div.row > div:nth-child(2) > a"
    links = []
    i = 0
    #Quantidade de noticias
    while len(links) < 20:
        #encontra apenas os elementos que sao noticias
        elements = driver.find_elements_by_css_selector(news_path)
        #retorna os links dos elementos utilizando list comprehension 
        links = [element.get_attribute('href') for element in elements]
        #print("Iteracao: " + str(i))
        #print("Quantidade de links: " + str(len(links)))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        driver.get(driver.current_url[:-1] + str(i))
        
        time.sleep(1)
        i += 1
        
    return links


def getListOfNewsLinksGameVicio(driver):
    #caminho unico para as noticias utilizando css selector
    news_path = "[class *= 'news-list'] > div > div > a:nth-child(1)"
    links = []
    #i = 0
    #Quantidade de noticias
    while len(links) < 20:
        #encontra apenas os elementos que sao noticias
        elements = driver.find_elements_by_css_selector(news_path)
        #retorna os links dos elementos utilizando list comprehension 
        links = [element.get_attribute('href') for element in elements]
        #print("Iteracao: " + str(i))
        #print("Quantidade de links: " + str(len(links)))

        #Procura e clicka no botao para exibir mais links para ser raspado
        actions = ActionChains(driver)
        btnLoadMorePages_element = driver.find_element_by_css_selector('#news-list-bt') 
        actions.move_to_element(btnLoadMorePages_element).perform()
        btnLoadMorePages_element.click()

        time.sleep(1)
        #i += 1
        
    return links

def getListOfNewsLinksIGN(driver):
    #caminho unico para as noticias utilizando css selector
    news_path = "[class *= 'NEWS']"
    links = []
    #i = 0
    #Quantidade de noticias
    while len(links) < 20:
        #encontra apenas os elementos que sao noticias
        elements = driver.find_elements_by_css_selector(news_path)
        #retorna os links dos elementos utilizando list comprehension 
        links = [element.find_elements_by_tag_name("a")[0].get_attribute('href') for element in elements]
        #print("Iteracao: " + str(i))
        #print("Quantidade de links: " + str(len(links)))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        #i += 1
        
    return links

def getCountComments(driver):
    #Rola a pagina pra baixo para que o iframe dos comentarios seja gerado
    for i in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
    
    totalFrames = driver.find_elements_by_tag_name("iframe")
    countComments_path = "[class = 'publisher-nav-color'] > [class = 'comment-count']"
        
    #i = 0
    for frame in totalFrames:
        #print("frame: " + str(i))
        driver.switch_to.default_content()
        try:
            driver.switch_to.frame(frame)
            countComments_element = driver.find_element_by_css_selector(countComments_path)
            countComments = countComments_element.text
            #print("Encontrou o elemento no frame: " + str(i))
            driver.switch_to.default_content()
            break
        except:
            continue
            #print("Elemento nao pertence a este frame")
        #i += 1
        #print("\n")
    
    driver.switch_to.default_content()
    return countComments

def scrapingData(driver, links, css_selector_paths, page):
    
    #cria uma lista vazia que recebera uma lista de dados a cada iteração
    listDataNews = []
    linkScrapedFailed = []
    #Entra em cada uma das paginas para fazer a raspagem
    for link in links:
        try:
            driver.get(link)
            time.sleep(2)
            
            #lista que contem os dados extraidos de uma pagina
            newsData = []
            
            #pega as informacoes do artigo
            
            #raspa e adiciona o Titulo do artigo
            title = driver.find_element_by_css_selector(css_selector_paths['title_path']).text
            newsData.append(title)
            print("Raspou o titulo com sucesso \n")
            
            #raspa e adiciona o SubTitulo do artigo
            subTitle = driver.find_element_by_css_selector(css_selector_paths['subTitle_path']).text
            newsData.append(subTitle)
            print("Raspou o SubTitulo com sucesso \n")
            
            #raspa e adiciona o Autor do artigo
            author = driver.find_element_by_css_selector(css_selector_paths['author_path']).text
            newsData.append(author)
            print("Raspou o Autor com sucesso \n")
            
            print("page = " + page)
            #raspa e adiciona a data do artigo
            if page == 'IGN' or page == 'Adrenaline':
                date = driver.find_element_by_css_selector(css_selector_paths['date_path']).text
            elif page == 'GameVicio':
                print("entrou no page GameVicio")
                date = driver.find_element_by_css_selector(css_selector_paths['date_path']).get_attribute('title')
            
            newsData.append(date)
            print("Raspou a data do artigo com sucesso \n")
            
            #raspa e adiciona a quantidade de comentarios a lista
            nComments = getCountComments(driver)
            newsData.append(nComments)
            print("Raspou a quantidade de comentarios com sucesso \n")
            
            #adiciona a data e hora de extracao
            now = datetime.now()
            newsData.append(now.strftime("%d/%m/%Y %H:%M:%S"))
            print("Data e hora da extracao adicionadas com sucesso")
            
            #adiciona a URL do artigo a lista 
            newsData.append(link)
            print("URL da pagina adicionada com sucesso")
            
            #adiciona os dados da raspagem em uma lista auxiliar
            listDataNews.append(newsData)
            print("Fim da raspagem da pagina com sucesso")
        except:
            print("link: " + link)
            print("Erro inesperado, armazena link que deu errado e pula para a proxima noticia")
            linkScrapedFailed.append(link)
            
    return listDataNews, linkScrapedFailed

def returnOnlyNewLinks(links, page):

    if page == 'IGN':
        df_news_database = pd.read_csv('C:\\Users\\yoliveira\\Desktop\\scrapingNews\\NewsIGN.csv', delimiter = '|', usecols = ['URL'])
    elif page == 'GameVicio':
        df_news_database = pd.read_csv('C:\\Users\\yoliveira\\Desktop\\scrapingNews\\NewsGameVicio.csv', delimiter = '|', usecols = ['URL'])
    elif page == 'Adrenaline':
        df_news_database = pd.read_csv('C:\\Users\\yoliveira\\Desktop\\scrapingNews\\Adrenaline.csv', delimiter = '|', usecols = ['URL'])
    
    linksToScrap = []
    #links da base de dados
    list_url = list(df_news_database['URL'])
    #percorra os links novos e verifique quais nao estao na base de dados
    for link in links:
        if link not in list_url:
            linksToScrap.append(link)
    return linksToScrap

def cleanColumnComments(df_news):
    #Remove caracteres e deixa apenas numeros na coluna comentarios
    df_news['nComments'] = df_news.nComments.apply(lambda x: unidecode.unidecode(x)) #tira acentuacao
    df_news['nComments'] = df_news.nComments.apply(lambda x: re.sub('[a-zA-Z]+', ' ', x)) #tira caracteres utilizando regex
    df_news[['nComments']] = df_news[['nComments']].astype(int) #transforma coluna nComentarios para tipo int
    return df_news

def replacePipe(df_news):
    #substitui o pipe da coluna titulo para que nao interfira no delimitador do csv
    df_news['Title'] = df_news.Title.apply(lambda x: x.replace('|', '-'))
    df_news['SubTitle'] = df_news.SubTitle.apply(lambda x: x.replace('|', '-'))
    df_news['DateExtraction'] = df_news.DateExtraction.apply(lambda x: x.replace('|', '-'))
    return df_news