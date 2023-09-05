# Dockerfile

FROM python:3.11

RUN mkdir /Screener
WORKDIR /Screener

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .