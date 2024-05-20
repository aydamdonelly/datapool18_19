import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

# Load the data
df = pd.read_csv('../transfer_data.csv')

# Process data
df['Fee'] = pd.to_numeric(df['Fee'], errors='coerce').fillna(0)
big6_clubs = ['Liverpool', 'Manchester United', 'Manchester City', 'Chelsea', 'Arsenal', 'Tottenham Hotspur']
df_big6 = df[df['Club'].isin(big6_clubs)]
seasons = sorted(df['Season'].unique())

def layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Big 6 Club Transfer Incomes and Expenses", className="text-center my-4")
            ])
        ]),
        dbc.Row([
            dbc.Col([
                html.Label('Select Seasons:', style={'fontWeight': 'bold'}),
                dcc.RangeSlider(
                    id='season-slider',
                    min=0,
                    max=len(seasons) - 1,
                    value=[0, len(seasons) - 1],
                    marks={i: season for i, season in enumerate(seasons)},
                    step=1
                )
            ], width=10, className="offset-md-1")
        ]),
        dbc.Row([
            dbc.Col([
                html.Label('Select Transfer Type:', style={'fontWeight': 'bold'}),
                dcc.RadioItems(
                    id='transfer-type-radio',
                    options=[
                        {'label': 'Incomes', 'value': 'Arrival'},
                        {'label': 'Expenses', 'value': 'Departure'}
                    ],
                    value='Arrival',
                    inline=True
                )
            ], width=10, className="offset-md-1")
        ]),
        dbc.Row([
            dbc.Col([
                html.Label('Select Clubs:', style={'fontWeight': 'bold'}),
                dcc.Checklist(
                    id='club-checklist',
                    options=[{'label': club, 'value': club} for club in big6_clubs],
                    value=big6_clubs,
                    inline=True
                )
            ], width=10, className="offset-md-1")
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='area-plot', config={'displayModeBar': False})
            ], width=12)
        ])
    ], fluid=True, style={'padding': '20px'})

def register_callbacks(app):
    @app.callback(
        Output('area-plot', 'figure'),
        [
            Input('season-slider', 'value'),
            Input('transfer-type-radio', 'value'),
            Input('club-checklist', 'value')
        ]
    )
    def update_area_plot(selected_seasons, selected_transfer_type, selected_clubs):
        filtered_seasons = seasons[selected_seasons[0]:selected_seasons[1] + 1]

        filtered_df = df_big6[
            (df_big6['Season'].isin(filtered_seasons)) &
            (df_big6['Transfer'] == selected_transfer_type) &
            (df_big6['Club'].isin(selected_clubs))
        ]

        fig = go.Figure()

        for club in selected_clubs:
            club_data = filtered_df[filtered_df['Club'] == club]
            club_data = club_data.groupby('Season').agg({'Fee': 'sum'}).reset_index()

            fig.add_trace(go.Scatter(
                x=club_data['Season'],
                y=club_data['Fee'],
                mode='lines',
                name=club,
                fill='tozeroy'
            ))

        fig.update_layout(
            title=f'Big 6 Club Transfer {selected_transfer_type}s per Season',
            xaxis_title="Season",
            yaxis_title="Total Fee (in Million €)",
            xaxis={'type': 'category'},
            font=dict(color='black'),
            plot_bgcolor='white',
            paper_bgcolor='white',
            legend_title_text='Club',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        return fig
