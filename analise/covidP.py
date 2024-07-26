import dash
import pandas as pd
from dash import dcc, Input, Output, html,Dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash_bootstrap_templates import ThemeSwitchAIO
import plotly.graph_objects as go

df=pd.read_csv("owid-covid-data-checkpoint-Copy1.csv")

#tratamento da base
for column in df.columns:
    df[column]=df[column].ffill()
df["date"]=pd.to_datetime(df["date"])
df["ano"]=df["date"].dt.year
df["ano"]=df["ano"].astype(str)
#rodar o programa

#themes

url_themes1=dbc.themes.DARKLY
url_themes2=dbc.themes.VAPOR
tema1="darkly"
tema2="vapor"

app=Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#settings of graphs
tabcard={"height": "100%"}
config_graph={"displayModeBar": False, "showTips":False}

#dropdowns
continentes=df["continent"].unique()
anos=df["ano"].unique().astype(int)

app=Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout=dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Row(
                html.H1("Covid-19"),
            ),
            dbc.Row([
                dbc.Col(
                    html.H3("Temas")
                ),
                dbc.Col([
                    ThemeSwitchAIO(aio_id="themes", themes=[url_themes1, url_themes2])
                ])
            ]),
            html.Br(),
            dbc.Row([
                html.H4("continentes"),
                dcc.Dropdown(continentes, id="continent", value="North America", style={"color": "black"} )
            ]),
            dbc.Row([
                html.H4("Paises"),
                dcc.Dropdown(id="countries", style={"color": "black"})
            ]),
            dbc.Row([
                html.H3("Ano"),
                dcc.RangeSlider(
                    id="anos",
                    min=2020,
                    max=2022,
                    step=1,
                    value=anos,
                    marks={i: f'{i}' for i in range(2020, 2023, 1)},
                    count=1
                )
            ])

            
        ],align="center",md=3, style={"height":"100vh"}, ),
                
        dbc.Col([
            dbc.Row(
                html.H3("Gráficos da covid-19", style={"textAlign": "center"})
            ),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(id='deaths_year', className="dbc",config=config_graph)
                        )
                    ,style= tabcard)
                ], md=6),
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(id="cases_year", className="dbc",config=config_graph)
                        )
                    , style= tabcard)
                ], md=6)
            ], className="g-2 my-auto", style={"margin-top": "7px"}),
            dbc.Row([
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                            dbc.Row(
                                html.H3("Total de Morte", style={"textAlign": "center"})
                            ),
                            dbc.Row(
                                dcc.Graph(id="total_deaths",  className="dbc",config=config_graph)
                            )
                        ])
                    , style=tabcard)
                ], md=4),
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                             dbc.Row(
                                html.H3("Total de Casos", style={"textAlign": "center"})
                            ),
                            dbc.Row([
                                dcc.Graph(id="total_cases", className="dbc",config=config_graph)
                            ])
                        ])
                    , style=tabcard)
                ], md=4),
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                            dbc.Row(
                                html.H3("Total de Vacinados", style={"textAlign": "center"})
                            ),
                            dbc.Row(
                                dcc.Graph(id="total_vacinated", className="dbc",config=config_graph)
                            )
                            
                        ])
                    , style=tabcard)
                ], md=4)

            ], className="g-2 my-auto", style={"margin-top": "7px"}),
            dbc.Row([
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(id="contry_deaths")
                        )
                    , style=tabcard)
                ], md=6),
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(id="population")
                        )
                    , style=tabcard)
                ], md=6)
            ], className="g-2 my-auto", style={"margin-top": "7px"}),    
        ],md=9, style={"height":"100hv"})
    ])
], fluid=True, style={"height": "100hv"})

@app.callback(
Output("countries","options"),
Input("continent", "value")
)
def updateOptionsDrop(contnent):
    continenteD=df.loc[df["continent"]==contnent]
    pais=continenteD["location"].unique()
    return [{"label":i, "value": i} for i in pais]

@app.callback(
Output("countries", "value"),
Input("countries", "options")
)
def updateFirstValue(countries):
    return [c["value"] for c in countries][1]

@app.callback(
    [Output("deaths_year", "figure"),
     Output("cases_year", "figure")],
    [Input("continent", "value"),
     Input("countries", "value"),
     Input("anos", "value"),
     Input(ThemeSwitchAIO.ids.switch("themes"), "value")]
)
def updateDeathsYear(continent, contries, years, toggle):
    if toggle:
        template=tema1
    else:
        template=tema2
    df["ano"]=pd.to_numeric(df["ano"])
    dff=df.loc[(df["continent"]== continent) & (df["location"]==contries) & (df["ano"].between(years[0], years[2]))]
    dff=dff.sort_values(by="date")
    fig1=px.line(dff,x="date", y="total_deaths", template=template, title=f"Números de mortes durante todo o ano em {contries}")
    fig2=px.histogram(dff,x="date", y="total_cases", template=template, title=f"Números de casos durante todo o ano em {contries}")
    return fig1, fig2

@app.callback(
    [Output("total_deaths", "figure"),
    Output("total_cases", "figure"),
    Output("total_vacinated", "figure")],
    [[Input("continent", "value"),
     Input("countries", "value"),
     Input("anos", "value"),
     Input(ThemeSwitchAIO.ids.switch("themes"), "value")]]
)
def update_indicators(continent, contries, years, toggle):
    if toggle:
        template=tema1
    else:
        template=tema2
    df["ano"]=pd.to_numeric(df["ano"])
    dff=df.loc[(df["continent"]== continent) & (df["location"]==contries) & (df["ano"].between(years[0], years[2]))]
    df_deaths=dff.sort_values(by="total_deaths", ascending=False)
    total_deaths=df_deaths["total_deaths"].iloc[0]
    total_deaths2=df_deaths["total_deaths"].iloc[1]
    fig1=go.Figure(go.Indicator(
        mode="number+delta",
        value=total_deaths,
        delta={"reference": total_deaths2},
        domain={"x":[0,1], "y":[0,1]}
    ))

    fig1.update_layout(template=template)
    df_cases=dff.sort_values(by="total_cases", ascending=False)
    total_cases=df_cases["total_cases"].iloc[0]
    total_cases2=df_cases["total_cases"].iloc[1]
    fig2=go.Figure(go.Indicator(
        mode="number+delta",
        value=total_cases,
        delta={"reference": total_cases2},
        domain={"x":[0,1], "y":[0,1]},
    ))
    fig2.update_layout(template=template)

    df_vacinated=dff.sort_values(by="total_vaccinations", ascending=False)
    total_vacinated=df_vacinated["total_vaccinations"].iloc[0]
    total_vacinated2=df_vacinated["total_vaccinations"].iloc[1]
    fig3=go.Figure(go.Indicator(
        mode="number+delta",
        value=total_vacinated,
        delta={"reference": total_vacinated2},
        domain={"x":[0,1], "y":[0,1]},
    ))
    fig3.update_layout(template=template)
    return fig1, fig2, fig3


@app.callback(
    [Output("contry_deaths", "figure"),
     Output("population", "figure")],
    [Input("continent", "value"),
     Input("countries", "value"),
     Input("anos", "value"),
     Input(ThemeSwitchAIO.ids.switch("themes"), "value")]
)
def update_lastfigs(continent, countries,  years, toggle):
    if toggle:
        template=tema1
    else:
        template=tema2
    df["ano"]=pd.to_numeric(df["ano"])
    dff=df.loc[(df["continent"]==continent) & (df["ano"].between(years[0], years[2]))]
    dff2=df.loc[(df["continent"]==continent) & (df["location"]==countries) & (df["ano"].between(years[0], years[2]))]
    dfeditor=dff[["location", "new_deaths"]].groupby("location").sum().reset_index()
    sortedValues=dfeditor.sort_values(by="new_deaths", ascending=False).head(6)
    fig1=px.bar(sortedValues, x="location", y="new_deaths")
    
    
    maior_menor=dff2.sort_values(by="total_vaccinations", ascending=False)
    total=maior_menor["total_vaccinations"].iloc[0]

    maior_menor2=dff2.sort_values(by="population", ascending=False)
    total2=maior_menor2["population"].iloc[0]

    rótulos  =  [ "vacinados", "Nao vacinados" ]
    valores  =  [ total, total2  ]
    fig2  =  go . Figure ( data = [ go . Pie ( labels = rótulos ,  values = valores )]) 
    fig1.update_layout(template=template)
    fig2.update_layout(template=template)
    return fig1, fig2
    
app.run_server(debug=True, port=8051)