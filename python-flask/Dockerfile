FROM python:3-slim

WORKDIR /app

ADD requirements.txt ./
RUN pip install -r requirements.txt

CMD ["python", "-u", "app.py"]

ADD . ./

