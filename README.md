# Codal Data Scraper

This project is designed to extract data from the [Codal](https://codal.ir) platform. The goal of this tool is to collect financial and management information of companies from the reports published on this platform. This tool is built using Python and several libraries such as `Playwright`, `Requests`, and `Django`.

## Features

- Extract various data from Codal using different search filters
- Support for extracting data based on various parameters like company status, report type, etc.
- Store extracted data and errors in a database using Django
- Log and error management
- Support for concurrent operations using threading in Django

## Installation and Setup

To use this project, you need to set up an appropriate working environment:

```docker
docker build .
```
```docker
docker-compose build
```
After that, you can run Docker in detached mode:
```docker
docker-compose up -d
```
For setting up the database configurations:
```docker
docker-compose exec web python manage.py makemigrations 
```
```docker
docker-compose exec web python manage.py migrate
```
You can create a superuser with the following command:
```docker
docker-compose exec web python manage.py createsuperuser
```
If you want to run a script, follow this structure:
```docker
docker-compose exec web <youre scpript>
```
#### Search Instructions
To run the script, you need to use the POST method to send a request to the following URL:
```url
http://127.0.0.1:8000/start-scrape/
```
You need to send parameters in the request body. Here's an example:
```json
{
    "Audited": true,
    "CompanyType": 1,
    "IndustryGroup": 27,
    "Symbol": "فولاد",
    "name": "فولاد مبارکه اصفهان",
    "row_names": [["تختال", 1]],
    "col_names": ["مبلغ بهای تمام شده", 2]
}

```
##### "row_names": [["تختال", 1]]
In essence, it indicates that the first row is named "تختال", and 1 could be used for purposes like numbering or ordering the rows.
##### "col_names": ["مبلغ بهای تمام شده", 2]
This structure shows that the first column is named "مبلغ بهای تمام شده", and 2 might be used for purposes like numbering or identifying the columns.

In summary, these data structures define the layout of a table, where rows and columns are identified by specific names and identifiers.
