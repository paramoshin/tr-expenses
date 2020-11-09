FROM python:3.9-buster

COPY requirements.txt /.
RUN pip install -r requirements.txt

COPY *.py ./
COPY createdb.sql ./

ENTRYPOINT ["python", "bot.py"]
