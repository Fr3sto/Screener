FROM python:3.11



ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY requirements.txt /Screener/requirements.txt
WORKDIR /Screener

RUN pip install -r requirements.txt

CMD ["gunicorn","-b","0.0.0.0:80001", "soaqaz.wsgi:application"]