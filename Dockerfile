# pull official base image
FROM python:3.11.4-slim-buster

# set work directory

RUN mkdir /usr/src/app
RUN mkdir /usr/src/app/staticfiles
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY app/requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY app .