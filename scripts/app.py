# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 01:38:12 2021

@author: yoliveira
"""
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

print("Rodando Adrenaline")
scrapingAdrenaline.mainAdrenaline(ip_docker_inspect_selenium)
print("Finalizando Adrenaline")

print("Rodando GameVicio")
scrapingGameVicio.mainGameVicio(ip_docker_inspect_selenium)
print("Finalizando GameVicio")

print("Rodando IGN")
scrapingIGN.mainIGN(ip_docker_inspect_selenium)
print("Finalizando IGN")