FROM amancevice/pandas:latest

RUN pip install selenium \
    pymongo[tls,srv] \
    unidecode

#RUN pip install pymongo[tls,srv]

#RUN pip install unidecode

#portas para o mongodb-atlas - Cloud
EXPOSE 8080
EXPOSE 80
EXPOSE 27018
EXPOSE 27019
EXPOSE 27017
EXPOSE 4444

RUN mkdir /app
COPY scripts /app
WORKDIR /app
CMD ["python3", "app.py"]
