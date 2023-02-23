FROM python:3.7-alpine

EXPOSE 5000
COPY . /login-service

WORKDIR /login-service

RUN pip3 install -r requirements.txt

CMD python3 ./main.py