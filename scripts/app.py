# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 01:38:12 2021

@author: yoliveira
"""

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import scrapingAdrenaline
import scrapingGameVicio
import scrapingIGN

#credenciais para validar no banco
#MongoDB - Atlas
#https://account.mongodb.com/account/login
#email: oliveirayuri10@hotmail.com
#senha: testandomongo123
#uri = 'mongodb+srv://test:test@scrapingnews.uvlhs.mongodb.net/scraping_news?retryWrites=true&w=majority'

ip_docker_inspect_selenium = '172.18.0.2'

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
options.add_argument("--no-sandbox")
options.add_argument("--headless")
driver = webdriver.Remote("http://" + ip_docker_inspect_selenium + ":4444/wd/hub", DesiredCapabilities.CHROME, options = options)
print("Driver iniciado com sucesso \n")

print("Rodando Adrenaline")
driver = scrapingAdrenaline.mainAdrenaline(driver)
print("Finalizando Adrenaline")

#driver = webdriver.Remote("http://" + ip_docker_inspect_selenium + ":4444/wd/hub", DesiredCapabilities.CHROME, options = options)
print("Rodando GameVicio")
driver = scrapingGameVicio.mainGameVicio(driver)
print("Finalizando GameVicio")

#driver = webdriver.Remote("http://" + ip_docker_inspect_selenium + ":4444/wd/hub", DesiredCapabilities.CHROME, options = options)
print("Rodando IGN")
driver = scrapingIGN.mainIGN(driver)
print("Finalizando IGN")

#Encerra o driver, as vezes da um bug de session ID do proprio Chrome,
#  mas nao interfere na execucao do processo, visto que acontece apenas nos final
#driver.close()