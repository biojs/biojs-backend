FROM python:2.7

COPY . .

RUN echo \
  && pip install -r requirements.txt
