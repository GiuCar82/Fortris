# Fortris integration API service

## Introduction
This project is developed to answer the technical challenge of building an integration API service in python with five endpoints. 

## Technologies
Technologies and modules used:
* python3.8
* docker-compose
* fastapi
* uvicorn
* requests
* bs4
* pytrends
* xmltodict

 ## Usage
To run the API service simply execute the command `docker-compose up` in the root directory. That will execute the API scripts and the Uvicorn web server to listen to `localhost:8000` for the API calls. 

If everything is working properly the API should deliver the welcome message: *"Welcome to the Fortris integration API service"*.

> NOTE: The program is tested with docker-compose 1.29

## First endpoint
With the 1st endpoint the API collect and return the average life expectancy from the data.cdc.gov webpage according to the sex, race and year provided.

An exception is risen whether the sex or the race input values are not inside the allowed ones.

How to call the API:

`/life_expectancy/{sex}/{race}/{year}`

*Example:* `localhost:8000/life_expectancy/Female/All Races/1970`

## Second endpoint
With the 2nd endpoint the API collect and return the unemployment rate for State from the www.bls.gov webpage.

An exception is risen when the State is not inside the ones found in the webpage.

How to call the API:

`/unemployment/{STATE}`

*Example:* `localhost:8000/unemployment/Alaska` 
