from flask import Flask, render_template
import requests

app = Flask(__name__, static_folder='css', template_folder='html')


def get_data(query):
    api_endpoint = "https://disease.sh/v3/covid-19"
    response = requests.get(f"{api_endpoint}/{query}")
    return response.json()
    

@app.route('/')
def home():

    world_data = get_data("all") # dict of world data
    countries_data = get_data("countries") # list of dicts of countries data
    
    # Store Data in Variables
    total_cases = '{:,}'.format(world_data["cases"])
    active_cases = '{:,}'.format(world_data["active"])
    deaths = '{:,}'.format(world_data["deaths"])
    recovered = '{:,}'.format(world_data["recovered"])
    
    # Calculating death and recovery rate
    d, r = world_data["deaths"], world_data["recovered"]
    death_rate = f"{round((d / (d + r)) * 100, 2)}%"
    recovery_rate = f"{round((r / (d + r)) * 100, 2)}%"

    countries = sorted(countries_data, key=lambda k: k['cases'], reverse=True) # sort the list based on total cases
    row_titles = ['#', 'Country', 'Total Cases', 'Deaths', 'Recovered', 'Active Cases', 'New Cases', 'New Deaths', 'Critical']
    keys = ['cases', 'deaths', 'recovered', 'active', 'todayCases', 'todayDeaths', 'critical']

    return render_template('index.html',
                           total_cases=total_cases,
                           active_cases=active_cases,
                           deaths=deaths,
                           recovered=recovered,
                           death_rate=death_rate,
                           recovery_rate=recovery_rate,
                           row_titles=row_titles,
                           countries=countries,
                           keys=keys,
                           )


if __name__ == '__main__':
    app.run(debug=True)
