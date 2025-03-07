FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

ENV FLASK_APP=run.py

CMD ["sh", "-c", "flask db upgrade && flask run --host=0.0.0.0 --port=5300"]