from flask import Flask, render_template
import covid
import plotly.express as ex
import plotly
import pandas as pd
import json
import numpy as np

app = Flask(__name__, static_folder='css', template_folder='html')


@app.route('/')
def home():
    data = covid.Covid(covid.config.WORLDOMETERS)  # Get data form Worldometers
    
    data_list = data.get_data()  # Returns list of data by country
    # Store Data in Variables
    total_cases = '{:,}'.format(data.get_total_confirmed_cases())
    active_cases = '{:,}'.format(data.get_total_active_cases())
    deaths = '{:,}'.format(data.get_total_deaths())
    recovered = '{:,}'.format(data.get_total_recovered())
    
    d, r = data.get_total_deaths(), data.get_total_recovered()
    death_rate = f"{round((d / (d + r)) * 100, 2)}%"
    recovery_rate = f"{round((r / (d + r)) * 100, 2)}%"

    countries = sorted(data_list, key=lambda k: k['confirmed'], reverse=True)
    row_titles = ['#', 'Country', 'Total Cases', 'Deaths', 'Recovered', 'Active Cases', 'New Cases', 'New Deaths',
                  'Critical']
    keys = ['confirmed', 'deaths', 'recovered', 'active', 'new_cases', 'new_deaths', 'critical']

    graphjson = graph(data_list, 'confirmed')

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
                           graphJSON=graphjson,
                           )


def graph(the_data, column):
    the_data[166]['country'] = 'Central African Republic' # Change the country name of 'CAR' for showing in the map
    df = pd.DataFrame(the_data)
    
    df.drop([0, 1, 2, 3, 4, 5, 6, 7], inplace=True)  # Drop unneccesary rows
    
    df['scaled'] = np.log10(df[column])    
        
    fig = ex.choropleth(data_frame=df,
                        title="Total Cases per country",
                        locations="country",
                        color= "scaled", 
                        color_continuous_scale="Blackbody_r", 
                        locationmode="country names",
                        labels={column: column.upper()}, 
                        hover_name="country", 
                        hover_data={'country': False, column: ':,', 'scaled': False})
    
    fig.update_layout(margin={'r': 0, 'l': 0, 'b': 0}, dragmode=False)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    
app.run(debug=True)
