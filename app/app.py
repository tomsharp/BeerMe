import dash
from flask_sqlalchemy import SQLAlchemy

## App Configuration

# - Dash -
# import external css
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#instanstiate the Dash object
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'BeerMe'

# - Flask -
# instanstiate the Flask object
server = app.server
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + ''

# - Flask-SQLAlchemy -
db = SQLAlchemy(server)


## App
import time

import dash_core_components as dcc
import dash_html_components as html 
from dash.dependencies import Input, Output, State

from util import *

# Layout
app.layout = html.Div([

    # css
    html.Link(href="app/assets/favicon.ico", rel="icon"),
    html.Link(rel="stylesheet", href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css",
              integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm",
              crossOrigin="anonymous"),
    html.Link(href='/assets/css/main.css', rel='stylesheet'),
    
    # url
    dcc.Location(id='url', refresh=False),


   html.Div(className = 'container my-4', children =[
        html.Div(id='search-section', className='card', children = [
            html.Div(className='card-body', children = [
                html.H2(className='card-title text-center', children = "Find My Beer"),
                html.Div(className='card-text text-center', children = [
                        """
                        Select up to 5 beers and our algorithm will predict which beer you should drink!
                        """
                ]),
                html.Div(className='row justify-content-center', children=[
                    html.Div(className='col-lg-5 m-4', children=[
                        dcc.Dropdown(
                            id = 'beer-selection-dropdown',
                            options = beer_options(),
                            multi = True
                        )
                    ]),
                ]),
                html.Div(className='row justify-content-center', children=[
                    html.Button('Search', id='search-button', className='btn btn-outline-primary')
                ]),
                html.Div(className='row justify-content-center my-3', children=[
                    html.Img(id='beer-loader', src='/assets/img/beer-loader.gif'),
                ]),
                 html.Div(className='row justify-content-center my-3', children=[
                    html.Div(id='search-results')
                ]),
            ]),
        ]),
    ]),
    # end container

])

## callbacks
@app.callback(Output('beer-loader', 'style'),
                [Input('search-button', 'n_clicks')],
                [State('beer-selection-dropdown', 'value')])
def display_beer_loader(n_clicks, value):
    if n_clicks != None and value != None and value != []:
        time.sleep(0.25)
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(Output('search-results', 'children'),
                [Input('search-button', 'n_clicks')],
                [State('beer-selection-dropdown', 'value')])
def display_beer_loader(n_clicks, value):
    print(value)
    if n_clicks != None and value != None and value != []:
        return "here"
    
    elif n_clicks != None:
        return ":( Please select at least one beer"

    else:
        pass



## run
if __name__ == '__main__':
    app.run_server(debug=True)