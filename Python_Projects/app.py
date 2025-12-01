
from dash import Dash, dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import load_figure_template

import plotly.express as px
import pandas as pd
import numpy as np

resorts = (
    pd.read_csv("../Data/Ski Resorts/resorts.csv", encoding = "ISO-8859-1")
    .assign(
        country_elevation_rank = lambda x: x.groupby("Country", as_index=False)["Highest point"].rank(ascending=False),
        country_price_rank = lambda x: x.groupby("Country", as_index=False)["Price"].rank(ascending=False),
        country_slope_rank = lambda x: x.groupby("Country", as_index=False)["Total slopes"].rank(ascending=False),
        country_cannon_rank = lambda x: x.groupby("Country", as_index=False)["Snow cannons"].rank(ascending=False),
    )).rename(columns={'Summer skiing': 'Summerskiing'})

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG, dbc_css])

load_figure_template('CYBORG')

app.layout = dbc.Container([dcc.Tabs([    
    dcc.Tab(label='Resort Map', className="custom-tab", selected_className="custom--selected", style={"background": "#1f2937","color": "white","padding": "10px"},selected_style={"background": "#1f2937", "color": "white", "fontWeight": "bold"},
            children=[html.Br(),
                    dbc.Row([dbc.Col(), dbc.Col(html.H5(id='map-title', style={'text-align':'center'}), width=9)]),
                    dbc.Row([
                        dbc.Col([dbc.Card(
                            [html.P('Price Limit', style={'fontWeight':'bold'} ),
                            dcc.Slider(id='price-slider', min=0, max=150, step=25, marks={i: {'label': f"${i}"} for i in range(0,151,50)}, value=50),
                            html.Br(),
                            html.P('Featured Preferences', style={'fontWeight':'bold'} ),
                            dcc.Checklist(id='summer-skiing', options=[{'label':'Has Summer Skiing', 'value':'Yes'}], value=[]),
                            dcc.Checklist(id='night-skiing', options=[{'label':'Has Night Skiing', 'value':'Yes'}], value=[]),
                            dcc.Checklist(id='snowparks', options=[{'label':'Has Snow Park', 'value':'Yes'}], value=[]), html.Br()
                            ]), html.Br(),html.Br(),html.Br(),html.Br(), html.Br(),html.Br(),html.Br(),html.Br(), html.Br(),html.Br(),html.Br(),html.Br(),]), 
                        dbc.Col(dcc.Graph(id='scatter-map', ), width=9)
                              ])
                     ]) ,


    dcc.Tab(label='Country Profiler',className="custom-tab", selected_className="custom--selected", style={"background": "#1f2937","color": "white","padding": "10px"},selected_style={"background": "#1f2937", "color": "white", "fontWeight": "bold"},
            children=[html.Br(),
                dbc.Row([dbc.Col(width=2), dbc.Col(html.H5(id='bar-title', style={'text-align':'center'}), width=7), dbc.Col()]),
                dbc.Row([
                    dbc.Col([
                        html.H6('Select A Continent'),
                        dcc.Dropdown(id='continent-selection', options=resorts['Continent'].unique(), value='Europe',className="dbc" ),
                        html.Br(),
                        html.H6('Select A Country'),
                        dcc.Dropdown(id='country-selection', value='Norway',className="dbc" ),
                        html.Br(),
                        html.H6('Select A Metric to Plot'),
                        dcc.Dropdown(id='metric-selection', options=resorts.columns[6:], value='Price',className="dbc" ), 
                        html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),html.Br()],width=2), 
                    dbc.Col(dcc.Graph(id='bar-chart', hoverData = {'points': [{'customdata': ['Hemsedal']}]}), width=7), 
                    dbc.Col([dbc.Row(html.H6("Resort Report Card", className='text-center mb-3', style={'text-align':'center'})),
                             dbc.Row([dbc.Col(dbc.Card('Resort Name',style={'fontSize':14}),width=5), dbc.Col(html.Div(id='name',))]),
                             dbc.Row([dbc.Col(dbc.Card('Elevation Rank',style={'fontSize':14}),width=5), dbc.Col(html.Div(id='elevation-rank',))]),
                             dbc.Row([dbc.Col(dbc.Card('Slope Rank',style={'fontSize':14}),width=5), dbc.Col(html.Div(id='slope-rank',))]),
                             dbc.Row([dbc.Col(dbc.Card('Price Rank',style={'fontSize':14}),width=5), dbc.Col(html.Div(id='price-rank',))]),
                             dbc.Row([dbc.Col(dbc.Card('Canon Rank',style={'fontSize':14}),width=5), dbc.Col(html.Div(id='cannon-rank',))]),
                             dbc.Row()],  className="report-card"

                    ),

            ])
        ])
])], fluid=True, style={"padding":"20px", 'width':1300}) 

@app.callback(
    Output('map-title', 'children'),
    Output('scatter-map', 'figure'),
    Output('country-selection', 'options'),
    Input('price-slider', 'value'),
    Input('summer-skiing', 'value'),
    Input('night-skiing', 'value'),
    Input('snowparks', 'value'),
    Input('continent-selection', 'value'),
)

def render_report(max_price, summer_option, night_option, snowpark_option, continent_selected):
    title = f'Resorts with prices less than ${max_price}'
    df = resorts.query("Price <= @max_price")
    if summer_option == 'Yes':
        df = resorts.query("Summerskiing == 'Yes'")
    if night_option == 'Yes':
        df = resorts.query("Nightskiing == 'Yes'") 
    if snowpark_option == 'Yes':
        df = resorts.query("Snowparks == 'Yes'")

    fig = px.scatter_map(df, lat='Latitude', lon='Longitude', size='Total slopes', color='Total slopes', zoom=3, hover_name='Country')
    fig.update_layout(paper_bgcolor="#1f2937", plot_bgcolor="#1f2937", font_color='white', margin={"t":40, "b":40, "l":40, "r":40},)
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    country_options = resorts[resorts['Continent']==continent_selected]['Country'].unique()
    return title, fig, country_options

@app.callback(
    Output('bar-title', 'children'),
    Output('bar-chart', 'figure'),
    Output('name', 'children'),
    Output('elevation-rank', 'children'),
    Output('slope-rank', 'children'),
    Output('price-rank', 'children'),
    Output('cannon-rank', 'children'),
    Input('continent-selection', 'value'),
    Input('country-selection', 'value'),
    Input('metric-selection', 'value'),
    Input('bar-chart', 'hoverData'),

)
def render_report2(continent, country, metric, hoverData):
    df = resorts.query("Continent == @continent and Country == @country")
    fig = px.bar(df.sort_values(f'{metric}', ascending=False).iloc[:10,:], x='Resort', y=metric, hover_name = 'Resort', custom_data= ['Resort'])
    fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    title = f'Top Resorts in {country} by {metric.title().replace('_', ' ')}'
    name = hoverData['points'][0]['customdata'][0]
    elevation = df[df['Resort']==name]['country_elevation_rank']
    slope = df[df['Resort']==name]['country_slope_rank']
    price = df[df['Resort']==name]['country_price_rank']
    cannon = df[df['Resort']==name]['country_cannon_rank']
    return title, fig, name, elevation, slope, price, cannon

if __name__ == '__main__':
    app.run(port=1102, debug=True)
