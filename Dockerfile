FROM python:3.8

WORKDIR /code

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY covidcache.py .

EXPOSE 5000

CMD [ "python", "./covidcache.py" ] 