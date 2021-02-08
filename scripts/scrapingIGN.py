# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 16:54:43 2021

@author: yoliveira
"""

from selenium import webdriver
import functions as func
import pandas as pd

def mainIGN():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--headless")
    driver = webdriver.Chrome("C:/chromedriver.exe", chrome_options = options)
    print("Driver iniciado com sucesso \n")
    
    driver.get('https://br.ign.com/')
    print("Requisicao para o site gameVicio com sucesso \n")
    
    #variavel que redireciona em alguns ifs do sistema e coloca os dados nas
    # colections corretas
    PAGE = "news_ign"
    
    #Pega os links das noticias da pagina 
    links = func.getListOfNewsLinksIGN(driver)
    #Estrategia Incremental, pega apenas os links que nao foram adicionados ainda
    links = func.returnOnlyNewLinks(links, PAGE)
    print("Pegou a lista de links que serao raspados com sucesso \n")
    
    #Faz scraping de 5 links por execucao.
    if len(links) > 5:
        links = links[0:5]
    
    #cria um dicionario contendo os paths dos elementos que serao raspados
    css_selector_paths = {'title_path':'#id_title', 'subTitle_path':'#id_deck',
                          'author_path':"[class = 'reviewer hcard'] > a",
                          'date_path':"[class='article-publish-date'] > span" }         
       
    
    #Roda duas vezes o scraping, uma pra todos e a segunda tentativa para aqueles
    # que deram erros
    listDataNews, linkScrapedFailed = func.scrapingData(driver, links, css_selector_paths, PAGE)
    print("Primeira tentativa de raspagem com sucesso \n")
    listDataNews2, linkScrapedFailed = func.scrapingData(driver, linkScrapedFailed, css_selector_paths, PAGE)
    print("Segunda tentativa de raspagem com sucesso \n")
    
    #junta os dados da primeira execucao com a lista dos que falharam na primeira
    listDataNews += listDataNews2
    
    if len(listDataNews) > 0:
        #tratamento e limpeza dos dados antes de armazenar na base de dados
        df_news = pd.DataFrame(listDataNews, columns = ['Title', 'SubTitle', 'Author',
                                                        'Date', 'nComments',
                                                        'DateExtraction','URL'])
        
        #Remove caracteres e deixa apenas numeros na coluna comentarios
        df_news = func.cleanColumnComments(df_news)
        #substitui o pipe da coluna titulo e SubTitulo para que nao interfira no delimitador do csv
        df_news = func.replacePipe(df_news)
        
        #Transforma os dados para o formato aceito pelo MongoDB(Dicionario)
        data = df_news.to_dict(orient='records')
        
        #mode = 'a' faz a inserção ser incremental, colocando apenas os dados novos, sem sobreescrever o csv
        #df_news.to_csv('C:\\Users\\yoliveira\\Desktop\\scrapingNews\\NewsIGN.csv', mode = 'a', sep = '|', index = False, header = False)
        #Insere novas linhas no MongoDB
        func.insertDataIntoMongo(data, PAGE)
    else:
        print("Nao existem dados para serem inseridos na base!")
    
    driver.close()
    print("Fim do programa")