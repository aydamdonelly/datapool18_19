import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Load the data from a CSV file
df = pd.read_csv('../transfer_data.csv')

# Convert 'Fee' to numeric, handling non-numeric data as NaN and then replacing NaN with 0
df['Fee'] = pd.to_numeric(df['Fee'], errors='coerce').fillna(0)

# Filter to include only the Big 6 clubs
big6_clubs = ['Liverpool', 'Manchester United', 'Manchester City', 'Chelsea', 'Arsenal', 'Tottenham Hotspur']
df_big6 = df[df['Club'].isin(big6_clubs)]

# Create a list of unique seasons
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
                html.Label('Select Seasons:', style={'fontWeight': 'bold', 'fontSize': '18px'}),
                dcc.RangeSlider(
                    id='season-slider',
                    min=0,
                    max=len(seasons) - 1,
                    value=[0, len(seasons) - 1],
                    marks={i: {'label': season, 'style': {'fontSize': '16px'}} for i, season in enumerate(seasons)},
                    step=1
                )
            ], width=10, className="offset-md-1 mb-4")
        ]),
        dbc.Row([
            dbc.Col([
                html.Label('Select Transfer Type:', style={'fontWeight': 'bold', 'fontSize': '18px'}),
                dcc.RadioItems(
                    id='transfer-type-radio',
                    options=[
                        {'label': 'Incomes', 'value': 'Arrival'},
                        {'label': 'Expenses', 'value': 'Departure'}
                    ],
                    value='Arrival',
                    inline=True,
                    inputStyle={'margin-right': '10px', 'transform': 'scale(1.5)'},
                    labelStyle={'margin': '10px'}
                )
            ], width=10, className="offset-md-1 mb-4", style={'marginTop': '15px'})
        ]),
        dbc.Row([
            dbc.Col([
                html.Label('Select Clubs:', style={'fontWeight': 'bold', 'fontSize': '18px'}),
                dcc.Checklist(
                    id='club-checklist',
                    options=[{'label': club, 'value': club} for club in big6_clubs],
                    value=big6_clubs,
                    inline=True,  # Keep horizontal alignment
                    inputStyle={'margin-right': '10px', 'transform': 'scale(1.5)'},
                    labelStyle={'margin': '10px'}
                )
            ], width=10, className="offset-md-1 mb-4", style={'marginTop': '20px'})
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='area-plot', config={'displayModeBar': False})
            ], width=12, style={'marginTop': '20px'})
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
                x=1,
                font=dict(size=14),
                itemclick=False,
                itemdoubleclick=False
            ),
            xaxis_tickfont=dict(size=16, family='Arial, sans-serif', weight='bold'),
            yaxis_tickfont=dict(size=16, family='Arial, sans-serif', weight='bold'),
            xaxis_title_font=dict(size=20, family='Arial, sans-serif', weight='bold'),
            yaxis_title_font=dict(size=20, family='Arial, sans-serif', weight='bold'),
            margin=dict(l=60, r=60, t=30, b=140),
            height=650  # Increased height for the chart
        )

        return fig
