# authors: Keanna Knebel
# date: 2020-08-06

###############################################################################
# IMPORT PACKAGES                                                             #
###############################################################################

# Basics
import pandas as pd
import numpy as np
import random
import json
import re
import os
from textwrap import dedent

# Plotly
import plotly.graph_objects as go
import plotly.express as px

# Dash
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

###############################################################################
# APP SET-UP                                                                  #
###############################################################################

app = dash.Dash(
    __name__, 
    meta_tags=[{"name": "viewport", "content": "width=device-width"}])

server = app.server

###############################################################################
# READ-IN DATASETS                                                            #
###############################################################################

df = pd.read_csv("data/mapped_ont_bcorps.csv")

mapbox_access_token = os.environ['map_box_key']

config={'displayModeBar': False}

industries = sorted(df.industry_category.unique())
categories = ["Overall Score", "Community", "Customers", 
              "Environment", "Governance", "Workers"]

###############################################################################
# LAYOUT                                                                      #
###############################################################################

app.layout = html.Div([
    
    # Main app header
    html.Div([
        # Setting the main title of the Dashboard
        html.H1(
            "Ontario B Corporations",
            className="app__title"
        )
    ]),

    # First row 
    html.Div(
        className="app__content",
        children=[

            # User input panel
            html.Div(
                className="one-fifth column",
                children=[
                    # drop-down menus
                    html.Div(
                        className="graph__container first",
                        children=[
                            html.P(
                                """Select a Business Industry:"""
                            ),

                            html.Div(
                                className="div-for-dropdown",
                                children=[
                                    dcc.Dropdown(
                                        id="industry-dropdown",
                                        options=[{'label': i, 'value': i} for i in industries],
                                        style={
                                            "border": "0px solid black"
                                        },
                                        placeholder='Select a business industry'
                                    )
                                ],
                            ),

                            html.P(
                                """Select an Impact Score Area:"""
                            ),

                            html.Div(
                                className="div-for-dropdown",
                                children=[
                                    dcc.Dropdown(
                                        id="score-dropdown",
                                        options=[{'label': i, 'value': i} for i in categories],
                                        style={
                                            "border": "0px solid black"
                                        },
                                        placeholder='Select an Impact Area'
                                    )
                                ],
                            ),
                        ],
                    ),

                    # Summary Industry Info side panel
                    html.Div(
                        id="summary_side_panel",
                        className="graph__container second",
                        style={"textAlign": "center",
                               "fontFamily": "sans-serif"}
                    ),
                ]
            ),
            # Ontario map container
            html.Div(
                className="two-thirds column graph__container map",
                children=[
                    dcc.Graph(
                        id='ont-map',
                        config=config
                    ),
                ],
            ),
            # Selected company info side panel
            html.Div(
                className="one-fifth column",
                children=[
                    html.Div(
                        className="graph__container third",
                        id="company_side_panel",
                        style={"textAlign": "center",
                               "fontFamily": "sans-serif"},
                    ),
                ]
            ),
        ],
    ),

    # Second row 
    html.Div(
        className="app__content",
        children=[

            # Industry bar chart container
            html.Div(
                className="one-half column graph__container",
                children=[
                    html.H4(
                        className="graph__title",
                        children=[
                            html.H4(
                                id="ind-title"),
                        ],
                    ),
                    dcc.Graph(
                        id='ind-graph',
                        config=config
                    ),
                ],
            ),
        ]
    ),
])

###############################################################################
# UPDATES + CALLBACKS                                                         #
###############################################################################

# Update the Ontario map
@app.callback(
    Output("ont-map", "figure"),
    [Input("industry-dropdown", "value"),
     Input("score-dropdown", "value")],
)
def update_map(sel_industry, sel_score):
    latInitial = 44
    lonInitial = -79
    zoom = 6
    opacity = 0.75

    if sel_industry:
        df_map = df[df.industry_category == sel_industry]
    else:
        df_map = df.copy()
    
    if (sel_score != 'Overall Score') and (sel_score):
        score_title = sel_score + " Impact Score"
        score_col = "impact_area_" + str.lower(sel_score)
    else:
        score_title = "Overall Impact Score"
        score_col = "overall_score"

    customdata = pd.DataFrame({
                'Business Name': df_map.company_name,
                'Industry': df_map.industry_category,
                'Cert': df_map.date_first_certified,
                'Impact Score' : df_map.overall_score})

    fig = (go.Figure(
            data=go.Scattermapbox(
                lat=df_map['lat'],
                lon=df_map['long'],
                mode="markers",
                customdata=customdata,
                marker=dict(
                    opacity=opacity,
                    size=9,
                    color=df_map[score_col],
                    colorscale='YlOrRd',
                    showscale=True,
                    colorbar=dict(
                        title=score_title,
                        titlefont=dict(
                            family='Open Sans',
                            size=16
                        ),
                        bgcolor="#404349",
                        x=1,
                        xanchor='left',
                        ticks="outside",
                        tickcolor="white",
                        tickwidth=2,
                    )
                ),
                hovertemplate=
                    "<b>%{customdata[0]}</b><br>" +
                    "<br>Industry: %{customdata[1]}" +
                    "<br>Certified since: %{customdata[2]}" +
                    "<br>Overall Impact Score: %{customdata[3]}" +
                    "<extra></extra>"
            ),

        layout=go.Layout(
            margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
            autosize=True,
            font={"color": "white"},
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center=dict(
                    lat=latInitial,
                    lon=lonInitial),
                style="dark",  
                zoom=zoom,
                bearing=0
            ),
        )
    ))

    fig.update_layout(clickmode='event+select')

    return fig

# Update the industry bar chart
@app.callback(
    [Output("ind-title", 'children'),
     Output("ind-graph", 'figure')],
    [Input("industry-dropdown", "value")],
)
def update_ind_graph(sel_industry):
    
    if sel_industry:
        title = "Number of Certified B Corporations in the " + sel_industry + " Industry, by Category"
        ind_df = df[df.industry_category == sel_industry]
        counts = ind_df.industry.value_counts()
    else:
        title = "Number of Certified B Corporations by Industry"
        counts = df.industry_category.value_counts()
    ind = list(counts.index)
    
    fig = go.Figure(
        data=go.Bar(
            y=ind,
            x=counts,
            marker_color='#FFDA67',
            hovertemplate="%{x}: %{y}<extra></extra>",
            orientation='h'),
        layout=go.Layout(
            margin={'l': 10, 'r': 10, 't': 10, 'b': 10},
            template='simple_white',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='grey',
            yaxis=go.XAxis(showticklabels=False),
            annotations=[
                dict(
                    x=xi,
                    y=yi,
                    text=yi,
                    xanchor="left",
                    yanchor="middle",
                    showarrow=False,
                )
            for xi, yi in zip(counts, ind)
            ],
        )
    )
    
    fig.update_layout(
            barmode='group',
            xaxis_title="Number of Businesses",
            yaxis_title="Industry",
            font=dict(
                color="white",
                size=14),
            height=550)
    fig.update_xaxes(showline=True, linewidth=2, linecolor='white')
    fig.update_yaxes(showline=True, linewidth=2, linecolor='white')
    
    return title, fig

# Update the summary side panel
@app.callback(
    Output("summary_side_panel", "children"),
    [Input("industry-dropdown", "value")],
)
def update_side_panel(sel_industry):

    # update title of the summary panel by industry
    if sel_industry:
        title = "the " + sel_industry + " Industry"
        sum_df = df[df.industry_category == sel_industry]
    else:
        title = "all Industries"
        sum_df = df.copy()
    
    # calculate number of B corporations
    num = len(sum_df)
    
    # calculate average impact scores
    total = round(sum_df.overall_score.mean(), 1)
    community = round(sum_df.impact_area_community.mean(), 1)
    environment = round(sum_df.impact_area_environment.mean(), 1)
    governance = round(sum_df.impact_area_governance.mean(), 1)
    workers = round(sum_df.impact_area_workers.mean(), 1)
    customers = round(sum_df.impact_area_customers.mean(), 1)

    # format html output for the summary stats
    sum_info = [
            # side panel title
            html.H4("Summary Statistics for",
                style={"marginBottom": 0}),
            html.H4(title, style={"marginTop": 0, "marginBottom": 0}),
            html.Hr(style={"marginTop": 5}),
            
            # number of certified businesses
            html.H3(num, style={"marginBottom": 0, "marginTop": 5}),
            html.H6("Businesses in Ontario"),
            
            # Impact scores table
            html.H4("__Average Impact Score__", 
                style={"marginBottom": 10,  "textDecoration": "underline"}),
            html.Div(
                children=[
                    html.H4("Overall Score: "),
                    html.H5("Community: "),
                    html.H5("Environment: "),
                    html.H5("Governance: "),
                    html.H5("Workers: "),
                    html.H5("Customers: ")
                ],
                style={"textAlign": "right", "width":"47%", 'display': 'inline-block'},
            ),
            html.Div(
                children=[
                    html.H4(total),
                    html.H5(community),
                    html.H5(environment),
                    html.H5(governance),
                    html.H5(workers),
                    html.H5(customers)
                ],
                style={"textAlign": "center", "width":"45%", 'display': 'inline-block'}
            ),
        ]

    return sum_info


# Update the selected company side panel
@app.callback(
    Output("company_side_panel", "children"),
    [Input("ont-map", "clickData")],
)
def update_company_side_panel(clickData):

    if clickData is not None:
        company_name = clickData['points'][0]['customdata'][0]
        company_df = df[df.company_name == company_name]

        # format html output
        sum_info = [
                html.H3(company_name),
                html.H6("Certified B Corporation since:", 
                    style={"marginBottom": 0}),
                html.H6(company_df.date_first_certified),
                html.H6(company_df.industry_category + " | " + company_df.industry),
                dcc.Markdown("[" + company_df.website + "](http://" + company_df.website + ")"),
                # Impact scores table
                html.H4("__Impact Score__", 
                    style={"marginBottom": 10,  "textDecoration": "underline"}),
                html.Div(
                    children=[
                        html.H4("Overall Score: "),
                        html.H5("Community: "),
                        html.H5("Environment: "),
                        html.H5("Governance: "),
                        html.H5("Workers: "),
                        html.H5("Customers: ")
                    ],
                    style={"textAlign": "right", "width":"47%", 'display': 'inline-block'},
                ),
                html.Div(
                    children=[
                        html.H4(company_df.overall_score),
                        html.H5(company_df.impact_area_community),
                        html.H5(company_df.impact_area_environment),
                        html.H5(company_df.impact_area_governance),
                        html.H5(company_df.impact_area_workers),
                        html.H5(company_df.impact_area_customers)
                    ],
                    style={"textAlign": "center", "width":"45%", 'display': 'inline-block'}
                ),
            ]
    else:
        sum_info = [html.H3("Select a company on the map to learn more")]

    return sum_info

if __name__ == '__main__':
    app.run_server(debug=True)