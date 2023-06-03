FROM python:3.10-slim-buster

WORKDIR /app

RUN pip3 install flask
COPY server.py ./
COPY run-server.sh ./

EXPOSE 8000

CMD ["bash", "./run-server.sh"]