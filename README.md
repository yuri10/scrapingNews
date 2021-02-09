# scrapingNews

Este projeto utiliza dois containers para fazer a raspagem das noticias. O primeiro é uma imagem do selenium-chrome e o outro é onde o script de scraping roda de fato. Neste segundo container, foi necessario instalar as bibliotecas: pandas(FROM amancevice/pandas), selenium(conexao remote), pymongo(Banco de Dados) e unidecode(tratamento nos dados).

Estou com planos, para futuras atualizacoes, de fazer um docker compose com os dois containers, pois diminuiria bastante o trabalho de executar o script. Entretanto, ja fiquei muito feliz de ter conseguido colocar minha aplicacao dentro de um docker e fazer se comunicar com um banco na nuvem e outro container local, foi uma experiência incrível.

* Passos para executar o projeto:

1. Baixe a imagem do selenium-chrome versão 3.141.59
~~~
$ sudo docker pull selenium/standalone-chrome:3.141.59
~~~~

2. Crie um network para fazer link entre os dois containers
~~~
$ sudo docker network create -d bridge selenium-app
~~~

3. Rode o container do selenium
~~~
$ sudo docker run -d -p 4444:4444 --network="selenium-app" --name selenium-3.141.59 selenium/standalone-chrome:3.141.59
~~~

4. Execute um inspect no container do selenium para pegar o ip
~~~
$ sudo docker inspect selenium-3.141.59
~~~
#pegue o IPAddress e guarde-o para colocar no script mais pra frente
~~~
"IPAddress": "172.18.0.2"
~~~

5. Clone este repositorio do git
~~~
$ git clone https://github.com/yuri10/scrapingNews.git
~~~

6. Abre o arquivo app.py (na pasta /scripts) e coloca o ip do inspect na variavel e salve o script.
~~~
ip_docker_inspect_selenium = "172.18.0.2"
~~~

7. Na raiz do diretorio clonado do git, builde o dockerfile do repositorio
~~~
$ sudo docker build -t scraping-news .
~~~~

8. Roda o container do projeto
~~~
$ sudo docker run --network="selenium-app" -e PYTHONUNBUFFERED=1 scraping-news
~~~


* Caso não queria utilizar os containers, você precisará das seguintes bibliotecas para rodar o projeto (/scripts/app.py):
*python 3.7 ou superior como base
*pandas #manipulação de dataframes
*selenium #raspagem dos dados
*unidecode #tratamento e limpeza de dados
*pymongo[srv] #conexao com o MongoDB - Atlas(cloud)
