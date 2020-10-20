#https://habr.com/ru/post/353234/
#docker build -t kwork_market:latest .
#docker run --name kwork --rm kwork_market:latest
#docker run --name kwork -v kwork_db:/site/app/data -d kwork_market:latest
#docker build -t kwork_market:latest .
#docker rm -f kwork;docker build -t kwork_market:latest . && docker run --name kwork -v kwork_db:/site/app/data -d kwork_market:latest

FROM python:3.6-alpine

ENV path /site

WORKDIR ${path}

COPY app/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app ${path}/app

ENV APP_PATH ${path}/app
ENV TOKEN_TG asd789asd78asdsada9sdsad

WORKDIR ${path}/app
#CMD tail -f /dev/null
CMD  python echoBot.py