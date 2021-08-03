FROM python:3.9.6

WORKDIR /app

ENV FLASK_APP=app.py FLASK_DEBUG=1 FLASK_RUN_HOST=0.0.0.0

COPY ./requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 5000

COPY . .

CMD ["flask", "run"]