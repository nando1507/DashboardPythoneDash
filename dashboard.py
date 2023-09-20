# Projeto 
# https://www.youtube.com/watch?v=LPvchXRbstA

# url dados
# https://covid.saude.gov.br/

# %pip install json
# %pip install requests
# %pip install pandas

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table, callback
from dash.dependencies import Input, Output, State
# from dash_bootstrap_templates import load_figure_template

import plotly.express as px
import plotly.graph_objects as go

import numpy as np
import pandas as pd
import json
import pyodbc
from sqlalchemy import create_engine

centroMapa = dict(lat=-15.7809896469116, lon=-47.7969589233398)

server = 'DESKTOP-UVIN3NU'
database = 'Particular'
username = 'sa'
password = '*casa123'

# Criação da string de conexão
# connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
#conn = pyodbc.connect(connection_string)
connection_string = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
engine = create_engine(connection_string)

query = " Select * from TbCoronaVirusBrasil With (nolock) where Municipio is null "

#dadoscodvi19 = requests.get('https://brasil.io/api/dataset/covid19/caso/data')
#dicCovid = json.loads(dadoscodvi19.content)
#dicCovid.keys()
#dicCovid['results'][0].keys()
#dfCodiv19 = pd.DataFrame(dicCovid ['results'])

df = pd.read_sql(query, engine)
df_states = df[(~df["Estado"].isna()) & (df["Codmun"].isna())]
df_states_ = df_states[df_states["Data"] == "2020-05-13"]
df_brasil = df[df["Regiao"]=="Brasil"]
df_data = df_states[df_states["Estado"] == "SP"]

#estados pais delimitações por coordenadas
brasil_states = json.load(open("geojson/brazil_geo.json","r"))

select_columns = {
    "CasosAcumulado":"Casos Acumulados",
    "CasosNovos":"Novos Casos",
    "ObitosAcumulado":"Óbitos Acumulados",
    "ObitosNovos":"Óbitos por dia"
}

# estilo
app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY])

# =======================================================
# mapa
fig = px.choropleth_mapbox(
        df_states_,
        locations="Estado",
        color="CasosNovos",
        geojson=brasil_states,    
        color_continuous_scale="Redor",
        opacity=0.4,
        hover_data={
                "CasosAcumulado": True, 
                "CasosNovos":True,
                "ObitosNovos":True,
                "Estado":True
            },
        center=centroMapa,
        zoom=4
    )
fig.update_layout(
    paper_bgcolor="#242424",
    autosize=True,
    margin=dict(l=0, r=0, t=0, b=0 ),
    showlegend=False,
    mapbox_style="carto-positron"
)
fig.update_layout(
    paper_bgcolor="#242424",
    autosize=True,
    margin=dict(l=0, r=0, t=0, b=0 ),
    showlegend=False,
    mapbox_style="carto-darkmatter"
)

# grafico de linhas
fig2 = go.Figure(layout={"template":"plotly_dark"})
fig2.add_trace(go.Scatter(
    x=df_data["Data"],
    y=df_data["CasosAcumulado"]
))
fig2.update_layout(
    paper_bgcolor="#242424",
    plot_bgcolor="#242424",
    autosize=True,
    margin=dict(l=10, r=10, t=10, b=10 ),
    showlegend=False
)

# =======================================================
server = app.server
titulo = "Dash Covid"
app.title = titulo

# =========  Layout  =========== #
app.layout = dbc.Container(
    dcc.Loading(
        id="loading-geral", 
        type="default",
        children=[
        dbc.Row([
        dbc.Col([
            html.Div([  
                html.Img(
                    id="logo",
                    # src = app.get_asset_url("logo_dark.png"),
                    src="https://avatars.githubusercontent.com/u/22230099?s=400&u=b23c156311be72f5c936cd19dc20ebe22748f792&v=4",
                    height=50
                ),
                html.H5(titulo),
                dbc.Button(
                    "Brasil",
                    color="primary",
                    id="location-button",
                    size="lg"
                ),
            ],
            style={
            }),
            html.P(
                "Informe a data na qual deseja obter informações",
                style={
                    "margin-top":"40px"
                }
            ),
            html.Div(
                id="Teste",children=[
                    dcc.DatePickerSingle(
                        id="Date-Picker",
                        min_date_allowed=df_brasil["Data"].min(),
                        max_date_allowed=df_brasil["Data"].max(),
                        initial_visible_month=df_brasil["Data"].min(),
                        date=df_brasil["Data"].max(),
                        display_format="DD/MM/YYYY",
                        style={
                            "border":"0px solid black"                            
                        }
                    )
                ]
            ),
            # linha Cards
            dbc.Row([
                dbc.Col([
                    #card Casos recuperados
                    dbc.Card([
                        dbc.CardBody([
                            html.Span("Casos Recuperados"),
                            html.H3(0, style={"color":"#1ABC9C"}, id="casos-recuperados-text"),
                            html.Span("Em Acompanhamento"),
                            html.H5(0, style={"color":"#BDC3C7"}, id="novos-recuperados-text"),
                        ])
                    ], color="light", outline=True, style={
                        "margin-top":"10px", 
                        "box-shadow":"0 4px 4px 0 rgba(0,0,0,0.15), 0 4px 20px 0 rgba(0,0,0,0.15)", 
                        "color":"#ffffff"
                    })
                ],md=4),
                #card Casos Confirmados Totais
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Span("Casos Confirmados"),
                            html.H3(0, style={"color":"#F1C40F"}, id="casos-Confirmados-text"),
                            html.Span("Em Confirmados"),
                            html.H5(0, style={"color":"#BDC3C7"}, id="novos-Confirmados-text"),
                        ])
                    ], color="light", outline=True, style={
                        "margin-top":"10px", 
                        "box-shadow":"0 4px 4px 0 rgba(0,0,0,0.15), 0 4px 20px 0 rgba(0,0,0,0.15)", 
                        "color":"#ffffff"
                    })
                ],md=4),
                #card Casos obito
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Span("Casos obito"),
                            html.H3(0, style={"color":"#C0392B"}, id="casos-obito-text"),
                            html.Span("obito na data"),
                            html.H5(0, style={"color":"#BDC3C7"}, id="novos-obito-text"),
                        ])
                    ], color="light", outline=True, style={
                        "margin-top":"10px", 
                        "box-shadow":"0 4px 4px 0 rgba(0,0,0,0.15), 0 4px 20px 0 rgba(0,0,0,0.15)", 
                        "color":"#ffffff"
                    })
                ],md=4),
            ]),
            html.Div([
                html.P(
                    "Informe a data a qual deseja obter informações:", 
                    style={"margin-top":"25px"}
                ),
                dcc.Dropdown(
                    id="location-dropdown",
                    options=[{"label":j, "value":i} for i, j in select_columns.items()],
                    value="CasosNovos",
                    style={"margin-top":"25"}
                ),
                #grafico linhas
                dcc.Graph(
                    id="lineGraph", 
                    figure=fig2
                )
            ]),
        ],
            md=5, 
            style={"padding":"40px" , "background-color":"#2C3E50"}),
        dbc.Col([
            #Carregamento de dados
            dcc.Loading(
                id="loading-1", 
                type="default",
                children=[
                    #grafico Mapa
                    dcc.Graph(
                        id="choropleth-map", 
                        figure=fig,
                        style={
                            "height":"100vh",
                            "margin-right":"10px"
                        }
                    )
                ]
            ),        
        ],md=7)
    ], 
        #no_gutters = True,
        className="mt-5",
    )
    ]), 
    fluid=True
)


# =============================
# interatividade

@app.callback(
    [
        Output("casos-recuperados-text","children"),
        Output("novos-recuperados-text","children"),
        Output("casos-Confirmados-text","children"),
        Output("novos-Confirmados-text","children"),
        Output("casos-obito-text","children"),
        Output("novos-obito-text","children"),
    ],
    [
        Input("Date-Picker","date"),
        Input("location-button","children")
    ]
)
def display_Status(date, location):
    if location=="BRASIL":
        df_data_on_date = df_brasil[df_brasil["Data"]==date]
    else:
        df_data_on_date = df_states[(df_states["Data"]==date) & (df_states["Estado"]==location)]
        
    Recuperadosnovos = str("-" if df_data_on_date["Recuperadosnovos"].isna().values[0] else f'{int( df_data_on_date["Recuperadosnovos"]):,}'.replace(",","."))
    EmAcompanhamentoNovos = "-" if df_data_on_date["EmAcompanhamentoNovos"].isna().values[0] else f'{int( df_data_on_date["EmAcompanhamentoNovos"]):,}'.replace(",",".")
    CasosAcumulado = "-" if df_data_on_date["CasosAcumulado"].isna().values[0] else f'{int( df_data_on_date["CasosAcumulado"]):,}'.replace(",",".")	
    CasosNovos = "-" if df_data_on_date["CasosNovos"].isna().values[0] else f'{int( df_data_on_date["CasosNovos"]):,}'.replace(",",".")	
    ObitosAcumulado = "-" if df_data_on_date["ObitosAcumulado"].isna().values[0] else f'{int( df_data_on_date["ObitosAcumulado"]):,}'.replace(",",".")	
    ObitosNovos	 = "-" if df_data_on_date["ObitosNovos"].isna().values[0] else f'{int( df_data_on_date["ObitosNovos"]):,}'.replace(",",".")

    return [
            Recuperadosnovos,
            EmAcompanhamentoNovos,
            CasosAcumulado,
            CasosNovos,
            ObitosAcumulado,
            ObitosNovos]

@app.callback(
    Output("lineGraph", "figure"),
    [
        Input("location-dropdown","value"),
        Input("location-button","children")
    ]
)
def plot_line_graph(plot_type, location):
    if location=="BRASIL":
        df_data_on_location = df_brasil
    else:
        df_data_on_location = df_states[df_states["Estado"]==location]

    fig2 = go.Figure(layout={"template":"plotly_dark"})
    bar_plots = ["CasosNovos","ObitosNovos"]

    if plot_type in bar_plots:
        fig2.add_trace(
            go.Bar(
                x=df_data_on_location["Data"],
                y=df_data_on_location[plot_type]
                )
            )
    else:
        fig2.add_trace(
            go.Scatter(
                x=df_data_on_location["Data"],
                y=df_data_on_location[plot_type]
                )
            )

    fig2.update_layout(
        paper_bgcolor="#242424",
        plot_bgcolor="#242424",
        autosize=True,
        margin=dict(l=10, r=10, t=10, b=10 ),
        # showlegend=False
    )
    return fig2

@app.callback(
    Output("choropleth-map", "figure"),
    [
        Input("Date-Picker","date")
    ]
)
def update_map(date):
    df_data_on_states = df_states[df_states["Data"]==date]

    fig = px.choropleth_mapbox(
        df_data_on_states,
        locations="Estado",
        color="CasosNovos",
        geojson=brasil_states,    
        color_continuous_scale="Redor",
        opacity=0.4,
        hover_data={
                "CasosAcumulado": True, 
                "CasosNovos":True,
                "ObitosNovos":True,
                "Estado":True
            },
        center=centroMapa,
        zoom=4
    )
    fig.update_layout(
        paper_bgcolor="#242424",
        autosize=True,
        margin=dict(l=0, r=0, t=0, b=0 ),
        showlegend=False,
        mapbox_style="carto-positron"
    )
    fig.update_layout(
        paper_bgcolor="#242424",
        autosize=True,
        margin=dict(l=0, r=0, t=0, b=0 ),
        showlegend=False,
        mapbox_style="carto-darkmatter"
    )
    return fig

@app.callback(
    Output("location-button","children"),
    [
        Input("choropleth-map","clickData"),
        Input("location-button","n_clicks")
    ]
)
def update_location(click_data, n_clicks):
    changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if click_data is not None and changed_id != "location-button.n_clicks":
        state=click_data["points"][0]["location"]
        return "{}".format(state)
    else:
        return "BRASIL"

# =========  Run server  =========== #
if __name__ == "__main__":
    app.run_server(
                    debug=True, 
                    #port = 8099
                )
