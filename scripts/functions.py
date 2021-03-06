# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 20:19:16 2021

@author: yoliveira
"""

from selenium.webdriver.support.ui import WebDriverWait #wait elements
from selenium.webdriver.common.by import By # 
from selenium.webdriver.support import expected_conditions as EC #wait for iframe
import pandas as pd #Manipulacao de dataframes
import time #insere alguns sleeps para esperar a pagina carregar. Posteriormente, mudar para os Waits do selenium
import re #regex para limpeza dos dados
import unidecode #limpeza e tratamento de dados
import sys #mudança de WORKDIR
from pymongo import MongoClient #Acesso ao banco de dados na nuvem
from datetime import datetime #pegar dia e hora em que houve a extração
from selenium.webdriver.common.action_chains import ActionChains #Rolar a pagina até um determinado elemento

def getListOfNewsLinksAdrenaline(driver):
    time.sleep(5)
    #caminho unico para as noticias de uma pagina Adrenaline(utilizando css selector)
    news_path = "article.post-h > div.row > div:nth-child(2) > a"
    links = []
    i = 1
    
    while len(links) < 150:
        #encontra apenas os elementos que sao noticias e adiciona numa lista(list comprehension)
        elements = driver.find_elements_by_css_selector(news_path)
        links_current_page = [element.get_attribute('href') for element in elements]
        
        #Rola a pagina pra baixo
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        #Junta os links das diversas iteracoes
        links += links_current_page
        print("pagina i: " + str(i))
        print("quantidade links: " + str(len(links)))
        i += 1
        #Pega a proxima pagina que contem mais noticias
        driver.get(driver.current_url[:-1] + str(i))
        time.sleep(3)
        
    return links, driver


def getListOfNewsLinksGameVicio(driver):
    time.sleep(5)
    #caminho unico para as noticias utilizando css selector
    news_path = "[class *= 'news-list'] > div > div > a:nth-child(1)"
    links = []

    while len(links) < 50:
        #encontra e retorna apenas os elementos que sao noticias(list comprehension )
        elements = driver.find_elements_by_css_selector(news_path)
        links = [element.get_attribute('href') for element in elements]
        
        #Procura e clicka no botao para exibir mais links para ser raspado
        actions = ActionChains(driver) 
        btnLoadMorePages_element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#news-list-bt')))
        actions.move_to_element(btnLoadMorePages_element).perform()
        btnLoadMorePages_element.click()

        time.sleep(2)
        
    return links, driver

def getListOfNewsLinksIGN(driver):
    time.sleep(5)
    #caminho unico para as noticias utilizando css selector
    news_path = "[class *= 'NEWS']"
    links = []
    
    #Enquanto a quantidade links capturados for menor do que a quantidade
    # definida, role a pagina pra baixo para carregar mais links
    while len(links) < 50:
        #encontra e retorna apenas os elementos que sao noticias(list comprehension)
        elements = driver.find_elements_by_css_selector(news_path)
        links = [element.find_elements_by_tag_name("a")[0].get_attribute('href') for element in elements]
        
        #rola a pagina pra baixo pra carregar mais links
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print("rolando a pagina da ign pra baixo")
        time.sleep(3)
        
    return links, driver

def getCountComments(driver):
    '''
    Esta funcao retorna a quantidade de comentarios que um artigo possui.
    Como os comentarios carregam de forma dinamica, é preciso rolar a pagina
    pra baixo para que o sistema de comentarios fique visivel. Além disso, os
    comentarios ficam em um iframe diferente do default, então é preciso procurar
    pelo elemento em cada iframe da pagina. 
    '''

    time.sleep(5)

    #Rola a pagina pra baixo para que o iframe dos comentarios seja gerado
    #precisa rolar duas vezes, coloquei 3 por garantia, pois as vezes a pagina nao responde corretamente
    for i in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    
    #pega referencia de todos iframes da pagina
    totalFrames = driver.find_elements_by_tag_name("iframe")
    #path, utilizando css selector, que tem a referencia da quantidade de comentarios
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
    return countComments, driver

def scrapingData(driver, links, css_selector_paths, PAGE):
    '''
    Funcao principal do programa. Recebe como parametro os links que serao raspados,
    os paths dos elementos e uma constante PAGE que redireciona em alguns ifs.
    Raspa: titulo, subtitulo, autor, data de publicacao, numero de comentarios e 
    alguns metadados como data de extracao e url da pagina.

    '''
    #cria uma lista vazia que recebera uma lista de dados a cada iteração
    listDataNews = []
    linkScrapedFailed = []
    #Entra em cada uma das paginas para fazer a raspagem
    for link in links:
        time.sleep(5)
        try:
            driver.get(link)
            time.sleep(2)
            print('Link que esta sendo raspado: ' + link)
            
            #lista que contem os dados extraidos de uma pagina
            newsData = []
            
            #pega as informacoes do artigo
            
            #raspa e adiciona o Titulo do artigo
            if PAGE == 'news_gameVicio':
                title = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector_paths['title_path']))).get_attribute('title')
            else:
                title = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector_paths['title_path']))).text
            newsData.append(title)
            print("Raspou o titulo com sucesso \n")
                
            #raspa e adiciona o SubTitulo do artigo
            subTitle = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector_paths['subTitle_path']))).text
            newsData.append(subTitle)
            print("Raspou o SubTitulo com sucesso \n")
            
            #raspa e adiciona o Autor do artigo
            author = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector_paths['author_path']))).text
            newsData.append(author)
            print("Raspou o Autor com sucesso \n")
            
            
            #raspa e adiciona a data do artigo
            if PAGE == 'news_ign' or PAGE == 'news_adrenaline':
                date = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector_paths['date_path']))).text
            elif PAGE == 'news_gameVicio':
                date = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector_paths['date_path']))).get_attribute('title')
            
            newsData.append(date)
            print("Raspou a data do artigo com sucesso \n")
            
            #raspa e adiciona a quantidade de comentarios a lista
            nComments, driver = getCountComments(driver)
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
            
    return listDataNews, linkScrapedFailed, driver

def returnOnlyNewLinks(links, PAGE):
    '''
    Estrategia de insercao de dados incremental.
    Coloca apenas dados que nao estao na base(MongoDB)
    '''
    
    #conecta com a base de dados na nuvem
    client = MongoClient('mongodb+srv://test:test@scrapingnews.uvlhs.mongodb.net/scraping_news?retryWrites=true&w=majority')
    
    urls_base = []
    #retorna lista com todos os links na base
    for url in client['scraping_news'][PAGE].find({},{ "URL":1 , "_id":0}):
      urls_base.append(url['URL'])
    
    linksToScrap = []
    #percorre os links novos e verifica quais nao estao na base de dados
    # retorna apenas os que nao estao
    for link in links:
        if link not in urls_base:
            linksToScrap.append(link)
    
    return linksToScrap

'''
#Quando minha base de dados era utilizando csv, utilizava esta funcao abaixo para verificar
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
'''
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

def insertDataIntoMongo(data, PAGE):
    '''
    Recebe um dataframe como argumento e insere na base
    '''
    client = MongoClient('mongodb+srv://test:test@scrapingnews.uvlhs.mongodb.net/scraping_news?retryWrites=true&w=majority')
    col = client['scraping_news'][PAGE]
    col.insert_many(data)
    