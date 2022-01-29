from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

covid_api_endpoint = "https://disease.sh/v3/covid-19"
ipgeolocation_api_endpoint = "https://ipgeolocation.abstractapi.com/v1"


def format_num(num):
    return "{:,}".format(int(num))


def get_covid_data(query):
    response = requests.get(f"{covid_api_endpoint}/{query}")
    return response.json()


def get_world_data():
    data = get_covid_data("all")
    data_dict = {
        "cases": format_num(data["cases"]),
        "active": format_num(data["active"]),
        "recovered": format_num(data["recovered"]),
        "deaths": format_num(data["deaths"]),
    }
    return data_dict


def get_all_countries_data():
    countries_data = get_covid_data("countries") # list of dicts of countries data
    countries = sorted(countries_data, key=lambda k: k['cases'], reverse=True) # sort the list based on total cases
    return countries


def get_users_location_data():
    # Getting User's Location
    if request.headers.getlist("X-Forwarded-For"):
        ip_address = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip_address = request.remote_addr
        
    response = requests.get(ipgeolocation_api_endpoint, params={
        'api_key': os.environ.get("IP_API_KEY"),
        'ip_address': ip_address,
        'fields': 'country,country_code,flag'
    })
    location = response.json()
    
    # Getting User's Country's covid data
    covid_data = get_covid_data(f"countries/{location['country_code']}")
    data_dict = {
        "country": location['country'],
        "flag_url": location['flag']['svg'],
        "cases": format_num(covid_data['cases']),
        "active": format_num(covid_data['active']),
        "recovered": format_num(covid_data['recovered']),
        "deaths": format_num(covid_data['deaths'])
    }
    return data_dict
    

@app.route('/')
def home():
    world_data = get_world_data()
    countries_data = get_all_countries_data()
    user_country_data = get_users_location_data()    
    return render_template('index.html',
                           world_data=world_data,
                           countries_data=countries_data,
                           user_country_data=user_country_data
                           )


if __name__ == '__main__':
    app.run(debug=True)
