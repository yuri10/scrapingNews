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
import re #regex para limpeza dos dados
import unidecode
from datetime import datetime #pegar dia e hora em que houve a extração

def getListOfNewsLinks():
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

def getCountComments():
    #Rola a pagina pra baixo para que o iframe dos comentarios seja gerado
    for i in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    
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
    
    return countComments

def scrapingData(links):
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
            title = driver.find_element_by_css_selector('#id_title').text
            newsData.append(title)
            
            #raspa e adiciona o SubTitulo do artigo
            subTitle = driver.find_element_by_css_selector('#id_deck').text
            newsData.append(subTitle)
            
            #raspa e adiciona o Autor do artigo
            author = driver.find_element_by_css_selector("[class = 'reviewer hcard'] > a").text
            newsData.append(author)
            
            #raspa e adiciona a data do artigo
            date = driver.find_element_by_css_selector("[class='article-publish-date']").text
            newsData.append(date)
            
            #raspa e adiciona a quantidade de comentarios a lista
            nComments = getCountComments()
            newsData.append(nComments)
            
            #adiciona a data e hora de extracao
            now = datetime.now()
            newsData.append(now.strftime("%d/%m/%Y %H:%M:%S"))
            
            #adiciona a URL do artigo a lista 
            newsData.append(link)
            
            #adiciona os dados da raspagem em uma lista auxiliar
            listDataNews.append(newsData)
        except:
            print("link: " + link)
            print("Erro inesperado, armazena link que deu errado e pula para a proxima noticia")
            linkScrapedFailed.append(link)
            
    return listDataNews, linkScrapedFailed

def returnOnlyNewLinks(links):
    '''
    Return a list
    -------
    Retorna uma lista contendo apenas os links que nao estao na base de dados
    e precisam ser raspados. Estrategia Incremental, apenas novos artigos 
    devem ser esccritos na base. 

    '''
    linksToScrap = []
    df_news_database = pd.read_csv('C:\\Users\\yoliveira\\Desktop\\scrapingNews\\NewsIGN.csv', delimiter = '|', usecols = ['URL'])
    list_url = list(df_news_database['URL'])
    for link in links:
        if link not in list_url:
            linksToScrap.append(link)
    return linksToScrap

        
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome("C:/chromedriver.exe", chrome_options = options)

driver.get('https://br.ign.com/')

#Pega os links das noticias da pagina 
links = getListOfNewsLinks()
#Estrategia Incremental, pega apenas os links que nao foram adicionados ainda
links = returnOnlyNewLinks(links)
            
#Roda duas vezes o scraping, uma pra todos e a segunda tentativa para aqueles que deram erros
listDataNews, linkScrapedFailed = scrapingData(links)
listDataNews2, linkScrapedFailed = scrapingData(linkScrapedFailed)

#junta os dados da primeira execucao com a lista dos que falharam na primeira
listDataNews += listDataNews2

#tratamento e limpeza dos dados antes de armazenar na base de dados
df_news = pd.DataFrame(listDataNews, columns = ['Title', 'SubTitle', 'Author', 'Date', 'nComments','DateExtraction','URL'])

#Remove caracteres e deixa apenas numeros na coluna comentarios
df_news['nComments'] = df_news.nComments.apply(lambda x: unidecode.unidecode(x)) #tira acentuacao
df_news['nComments'] = df_news.nComments.apply(lambda x: re.sub('[a-zA-Z]+', ' ', x)) #tira caracteres utilizando regex
df_news[['nComments']] = df_news[['nComments']].astype(int) #transforma coluna nComentarios para tipo int

#substitui o pipe da coluna titulo para que nao interfira no delimitador do csv
df_news['Title'] = df_news.Title.apply(lambda x: x.replace('|', '-'))
df_news['SubTitle'] = df_news.SubTitle.apply(lambda x: x.replace('|', '-'))

#antes de escrever os novos dados, fazemos um union entre os dados que acabaram
    # de ser raspados e os novos que já estão na base de dados.
df_news_database = pd.read_csv('C:\\Users\\yoliveira\\Desktop\\scrapingNews\\NewsIGN.csv', delimiter = '|')
df_news = pd.concat([df_news_database, df_news], ignore_index = True)

df_news.to_csv('C:\\Users\\yoliveira\\Desktop\\scrapingNews\\NewsIGN.csv', sep = '|', index = False)


print("Fim do programa")