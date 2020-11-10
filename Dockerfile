FROM python:3.9-buster

ENV TZ=Europe/Moscow

COPY requirements.txt /.
RUN pip install -r requirements.txt

COPY *.py ./
COPY createdb.sql ./
COPY history.csv ./

ENTRYPOINT ["python", "bot.py"]
