from fastapi import FastAPI, HTTPException
import requests
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
import json
from datetime import datetime, timedelta
import xmltodict


app = FastAPI()


@app.get("/")
async def root():
    return ("Welcome to the Fortris integration API service")


# First endpoint #
@app.get("/life_expectancy/{sex}/{race}/{year}")
async def life_expectancy(sex: str, race: str, year: int):
    """
        An API to collect the life expectancy of the population for sex, race and year from data.cdc.gov

    :param sex: Input sex
    :param race: Input race
    :param year: Input year
    :return: Life expectancy
    """
    # Raise and exception if the sex input value is not inside the allowed ones.
    if sex not in ["Female", "Male", "Both Sexes"]:
        raise HTTPException(status_code=404, detail="Wrong sex input value. The possible values are: 'Female', 'Male' "
                                                    "and 'Both Sexes'")
    # Raise and exception if the race input value is not inside the allowed ones.
    if race not in ["White", "Black", "All Races"]:
        raise HTTPException(status_code=404, detail="Wrong race input value. The possible values are: 'White', 'Black' "
                                                    "and 'All Races'")
    else:
        # Collect the response from the data.cdc.gov webpage according to the sex, race and year provided via API.
        response = requests.get(f"https://data.cdc.gov/resource/w9j2-ggv5.json?sex={sex}&race={race}&year={year}")
        # Parse the response into a json
        data = response.json()
        # Return the average life expectancy through the API.
        return {"average_life_expectancy": data[0]["average_life_expectancy"]}


# Second endpoint #
@app.get("/unemployment/{state}")
async def unemployment(state: str):
    """
        An API to collect the unemployment rate for State from www.bls.gov

    :param state: Input State (case sensitive)
    :return: Unemployment rate
    """
    # Initialize and empty dictionary to store the State along with the unemployment rate after the parsing of the HTML
    # table.
    data = {}
    # Collect the html of the webpage
    response = requests.get(f"https://www.bls.gov/web/laus/lauhsthl.htm")
    # Parse the html with BeautifulSoup
    html = BeautifulSoup(response.text, 'html.parser')
    # Extract the body of the table with the unemployment rate
    table_body = html.find("tbody")
    # Extract all the rows of the table
    rows = table_body.find_all('tr')
    # For each row extract the State name and the unemployment rate and insert them as key-value pair inside the
    # dictionary "data".
    for row in rows:
        data.update({row.find('th').text: row.find_all('td')[0].text})
    # Return the unemployment rate for the State passed through the API
    return {"rate": data[state]}


# Third endpoint #
@app.get("/trends")
async def trends(phrase: str,
           # When not provided the default start_date is the previous 2 weeks from the current date.
           start_date: str = (datetime.today() - timedelta(days=14)).strftime('%d-%m-%Y'),
           # When not provided the default end_date is the current date.
           end_date: str = datetime.today().strftime('%d-%m-%Y')):
    """
        An API to collect the trend for a phrase in Google Trends in a provided time frame.

    :param phrase: Input phrase
    :param start_date: Input start date. Format: %dd-%mm%-%YYYY
    :param end_date: Input end date. Format: %dd-%mm%-%YYYY
    :return:
    """
    # Initialize a new pytrend
    pytrend = TrendReq()
    # Collect the historical data from Google Trends for the input phrase between the start and end dates provided.
    historical_data_df = pytrend.get_historical_interest([phrase],
                                                         year_start=int(start_date[6:10]),
                                                         month_start=int(start_date[3:5]),
                                                         day_start=int(start_date[0:2]),
                                                         hour_start=0,
                                                         year_end=int(end_date[6:10]),
                                                         month_end=int(end_date[3:5]),
                                                         day_end=int(end_date[0:2]),
                                                         hour_end=0,
                                                         cat=0, geo='', gprop='', sleep=0, frequency='daily')
    # Convert the resulting pandas dataframe into a dictionary
    historical_data_dict = json.loads(historical_data_df.to_json())
    # Initialize the variable used to calculate the total interest
    total_interest = 0
    # Iterates the dictionary, to calculate summing the dictionary values, the total interest for the phrase in the
    # provided time frame.
    for v in historical_data_dict[phrase].values():
        total_interest += v
    # The total interest is returned from the API
    return {"interest": total_interest}

# Fourth endpoint #
@app.get("/weather")
async def weather():
    """

    An API to collect the historical weather for the last 7 days of the location where this client is connected
    to the Internet.

    :return: Location information and historical daily weather of the location.
    """
    # The start_date is 7 days from the current date.
    start_date = (datetime.today() - timedelta(days=6)).strftime('%Y-%m-%d')
    # The end_date is the current date.
    end_date = datetime.today().strftime('%Y-%m-%d')
    # Get the location of the client by the ip using the geolocation service ipinfo.io
    response = requests.get(f"http://ipinfo.io/json")
    geolocation = json.loads(response.text)
    # Extract the city from the geolocation response
    city = geolocation["city"]
    # Collect the response from api.weatherapi.com API
    response = requests.get(f"http://api.weatherapi.com/v1/history.xml?key=f61ffab5c57a4e2fa76100150223108&q={city}&dt={start_date}&end_dt={end_date}")
    # Convert the XML format to dictionary
    dict_data = xmltodict.parse(response.content)
    # Parse the dictionary to a new output JSON that maintains only the daily weather data along with the basics
    # location information
    for i in dict_data["root"]["forecast"]["forecastday"]:
        condition = i["day"].pop("condition")
        i["day"]["condition"] = condition["text"]

    json_data = \
        {"location": {"name": dict_data["root"]["location"]["name"],
                      "region": dict_data["root"]["location"]["region"],
                      "country": dict_data["root"]["location"]["country"]},
        dict_data["root"]["forecast"]["forecastday"][0]["date"]: dict_data["root"]["forecast"]["forecastday"][0]["day"],
        dict_data["root"]["forecast"]["forecastday"][1]["date"]: dict_data["root"]["forecast"]["forecastday"][1]["day"],
        dict_data["root"]["forecast"]["forecastday"][2]["date"]: dict_data["root"]["forecast"]["forecastday"][2]["day"],
        dict_data["root"]["forecast"]["forecastday"][3]["date"]: dict_data["root"]["forecast"]["forecastday"][3]["day"],
        dict_data["root"]["forecast"]["forecastday"][4]["date"]: dict_data["root"]["forecast"]["forecastday"][4]["day"],
        dict_data["root"]["forecast"]["forecastday"][5]["date"]: dict_data["root"]["forecast"]["forecastday"][5]["day"],
        dict_data["root"]["forecast"]["forecastday"][6]["date"]: dict_data["root"]["forecast"]["forecastday"][6]["day"]}

    return json_data

# Fifth endpoint #
@app.get("/trends_weather")
async def trends_weather(phrase: str):
    """
    An API to return the trends for a phrase in Google Trends and the weather data in the client location for the past 7
    days.

    A combination of the third and fourth endpoint.

    :param phrase:
    :return:
    """
    # NOTE: Pytreds has a bug (or behaviour) for which does not return the trends of the first 4 days from the
    # current date.

    # The start_date is 7 days from the current date (minus 4 as to find a workaround to pytreds bug and return 7 days).
    start_date = (datetime.today() - timedelta(days=10)).strftime('%Y-%m-%d')
    # The end_date is the current date (minus 4 days to as to find a workaround to pytreds bug and return 7 days).
    end_date = (datetime.today() - timedelta(days=4)).strftime('%Y-%m-%d')

    # TRENDS SECTION #
    # Initialize a new pytrend
    pytrend = TrendReq()
    # Collect the historical data from Google Trends for the input phrase between the start and end dates provided.
    historical_data_df = pytrend.get_historical_interest([phrase],
                                                         year_start=int(start_date[:4]),
                                                         month_start=int(start_date[5:7]),
                                                         day_start=int(start_date[8:10]),
                                                         hour_start=0,
                                                         year_end=int(end_date[:4]),
                                                         month_end=int(end_date[5:7]),
                                                         day_end=int(end_date[8:10]),
                                                         hour_end=0,
                                                         cat=0, geo='', gprop='', sleep=0, frequency='daily')
    # Convert the resulting pandas dataframe into a dictionary
    historical_data_dict = json.loads(historical_data_df.to_json(date_format='iso'))
    # Prepare the API output
    api_output = []
    for k, v in historical_data_dict[phrase].items():
        # Parse the date and insert it as key along with the trend
        api_output.append({"date": k[:10], "interest": v})

    # WEATHER SECTION #
    response = requests.get(f"http://ipinfo.io/json")
    geolocation = json.loads(response.text)
    # Extract the city from the geolocation response
    city = geolocation["city"]
    # Collect the response from api.weatherapi.com API
    response = requests.get(
        f"http://api.weatherapi.com/v1/history.xml?key=f61ffab5c57a4e2fa76100150223108&q={city}&dt={start_date}&end_dt={end_date}")
    # Convert the XML format to dictionary
    dict_data = xmltodict.parse(response.content)
    # Parse the dictionary to a new output JSON that maintains only the daily weather data along with the basics
    # location information
    for i in dict_data["root"]["forecast"]["forecastday"]:
        condition = i["day"].pop("condition")
        i["day"]["condition"] = condition["text"]

    json_data = \
        {"location": {"name": dict_data["root"]["location"]["name"],
                      "region": dict_data["root"]["location"]["region"],
                      "country": dict_data["root"]["location"]["country"]},
        dict_data["root"]["forecast"]["forecastday"][0]["date"]: dict_data["root"]["forecast"]["forecastday"][0]["day"],
        dict_data["root"]["forecast"]["forecastday"][1]["date"]: dict_data["root"]["forecast"]["forecastday"][1]["day"],
        dict_data["root"]["forecast"]["forecastday"][2]["date"]: dict_data["root"]["forecast"]["forecastday"][2]["day"],
        dict_data["root"]["forecast"]["forecastday"][3]["date"]: dict_data["root"]["forecast"]["forecastday"][3]["day"],
        dict_data["root"]["forecast"]["forecastday"][4]["date"]: dict_data["root"]["forecast"]["forecastday"][4]["day"],
        dict_data["root"]["forecast"]["forecastday"][5]["date"]: dict_data["root"]["forecast"]["forecastday"][5]["day"],
        dict_data["root"]["forecast"]["forecastday"][6]["date"]: dict_data["root"]["forecast"]["forecastday"][6]["day"]}

    for i in api_output:
        # Add the location information to the "weather" key
        i["weather"] = {"location": json_data["location"]}
        # Add the weather for the specified day in the "date" key
        i["weather"].update(json_data[i["date"]])

    return api_output

