FROM python:3.12.9

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# install playwrite lib requirements
RUN apt-get update && apt-get install -y \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libxtst6 \
    libxss1 \
    libnss3 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libx11-xcb1 \
    libgbm1 \
    libappindicator3-1 \
    libnspr4 \
    libx11-6 \
    libgdk-pixbuf-2.0-0


WORKDIR /code

COPY requirements.txt /code/

RUN pip install -r requirements.txt

RUN playwright install --with-deps

COPY . /code/
