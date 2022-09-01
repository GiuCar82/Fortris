# Fortris integration API service

## Introduction
This project is developed to answer the technical challenge of building an integration API service with five endpoints in python. 

## Technologies
The technologies and modules used are :
* python3.8
* docker-compose
* fastapi
* uvicorn
* requests
* bs4
* pytrends
* xmltodict

 ## Usage
 
To run the API service simply execute the command `docker-compose up` in the root folder. It will execute the python script and the Uvicorn web server to listen to `localhost:8000` for the API calls. 

## First endpoint
With the 1st endpoint the API gather and return the average life expectancy from the data.cdc.gov webpage according to the sex, race and year provided.

An exception is risen whether the sex or the race input values are not inside the allowed ones.

How to call the API:

`/life_expectancy/{sex}/{race}/{year}`
