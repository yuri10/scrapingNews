# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 22:58:03 2021

@author: yoliveira
"""


import functions as func
import pandas as pd


def mainAdrenaline(driver):  
    driver.get('https://adrenaline.com.br/noticias/pesquisa/todas/games/pagina/1')
    print("Requisicao para o site Adrenaline com sucesso \n")
    
    #variavel que redireciona em alguns ifs do sistema
    PAGE = 'news_adrenaline'
    
    #Pega os links das noticias da pagina 
    links, driver = func.getListOfNewsLinksAdrenaline(driver)
    print("Pegou a lista de links que serao raspados com sucesso \n")
    #Estrategia Incremental, pega apenas os links que nao foram adicionados ainda
    links = func.returnOnlyNewLinks(links, PAGE)

    print("Quantidade de links novos que nao existem na base: " + str(len(links)))
    
    #Faz scraping de 5 links por execucao.
    if len(links) > 5:
        links = links[0:5]
    print("Quantidade de links que serao raspados nessa execucao: " + str(len(links)))
    
    #cria um dicionario contendo os paths dos elementos que serao raspados
    css_selector_paths = {'title_path':"[class = 'news__title'] > h1",
                          'subTitle_path':"[class = 'news__title'] > span",
                          'author_path':"[class = 'news__info'] > span > strong > a",
                          'date_path':"[class = 'news__info'] > span:nth-child(2)" }         
    
    
    #Roda duas vezes o scraping, uma pra todos e a segunda tentativa para aqueles que deram erros
    listDataNews, linkScrapedFailed, driver = func.scrapingData(driver, links, css_selector_paths, PAGE)
    print("Primeira tentativa de raspagem com sucesso \n")
    listDataNews2, linkScrapedFailed, driver = func.scrapingData(driver, linkScrapedFailed, css_selector_paths, PAGE)
    print("Segunda tentativa de raspagem com sucesso \n")
    
    #junta os dados da primeira execucao com a lista dos que falharam na primeira
    listDataNews += listDataNews2
    
    #tratamento e limpeza dos dados antes de armazenar na base de dados
    df_news = pd.DataFrame(listDataNews, columns = ['Title', 'SubTitle', 'Author',
                                                    'Date', 'nComments',
                                                    'DateExtraction','URL'])
    
    if len(listDataNews) > 0:
        #Remove caracteres e deixa apenas numeros na coluna comentarios
        df_news = func.cleanColumnComments(df_news)
        #substitui o pipe da coluna titulo e subTitulo para que nao interfira no delimitador do csv
        df_news = func.replacePipe(df_news)
        
        #Transforma os dados para o formato aceito pelo MongoDB(Dicionario)
        data = df_news.to_dict(orient='records')
        
        #mode = 'a' faz a inserção ser incremental, colocando apenas os dados novos, sem sobreescrever o csv
        #df_news.to_csv('C:\\Users\\yoliveira\\Desktop\\scrapingNews\\Adrenaline.csv', mode = 'a', sep = '|', index = False, header=False)
        
        #Insere novas linhas no MongoDB
        func.insertDataIntoMongo(data, PAGE)
        print("inseriu no banco de dados")
    else:
        print("Nao existem dados para serem inseridos na base!")
    
    print("Fim do programa Adrenaline")
    return driver

