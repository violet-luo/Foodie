FROM python:3.7-alpine

EXPOSE 5000

WORKDIR /foodie-app

COPY . /foodie-app
RUN pip install -r requirements.txt

COPY app.py /foodie-app
CMD python app.py