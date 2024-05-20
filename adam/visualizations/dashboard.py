import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import dash_bootstrap_components as dbc
import base64
import os

# Load data for different visualizations
goals_df = pd.read_csv('../GOALS_ONLY_SORTED_UPDATED.csv')
players_df = pd.read_csv('../op_players_list_with_percentiles.csv')
transfers_df = pd.read_csv('../filtered_arrivals_with_additional_data.csv')
transfer_details_df = pd.read_csv('../transfer_data.csv')
club_results_df = pd.read_csv('../pl_club_results.csv')

# Helper function to convert images to base64 strings
def image_to_base64(image_path):
    with open(image_path, 'rb') as f:
        encoded_image = base64.b64encode(f.read()).decode('ascii')
    return 'data:image/png;base64,{}'.format(encoded_image)

# Process data for various visualizations
# Visualisierung 1: Top Scorers
goals_df['Cumulative Goals'] = goals_df.groupby('Player').cumcount() + 1
agg_df = goals_df.groupby(['MatchDay', 'Player', 'Squad']).size().reset_index(name='Goals')
agg_df['Cumulative Goals'] = agg_df.groupby(['Player', 'Squad'])['Goals'].cumsum()
total_goals = goals_df.groupby(['Player', 'Squad'])['Cumulative Goals'].max().reset_index()
top_10_players = total_goals.nlargest(10, 'Cumulative Goals')['Player'].tolist()
agg_df = agg_df[agg_df['Player'].isin(top_10_players)]
squad_colors = {
    'Liverpool': '#c8102e', 'Leicester City': '#003090', 'Manchester Utd': '#da291c',
    'Bournemouth': '#d71920', 'Wolves': '#fdb913', 'Tottenham Hotspur': '#d3d3d3',
    'Everton': '#003399', 'Crystal Palace': '#1b458f', 'Watford': '#fbec5d',
    'Manchester City': '#6cabdd', 'Newcastle Utd': '#241f20', 'Chelsea': '#034694',
    'Arsenal': '#ef0107'
}

# Visualisierung 2: Player Radar Charts
attacker_stats = [
    'Goals', 'Assists', 'Expected Goals', 'Expected Assisted Goals', 'Progressive Passes Received',
    'Shot creating actions', 'Crosses into penalty area', 'Successful take ons',
    'Goals per shot on target', 'Shots on target %', 'Aerial duels won %', 'Carries into final 1/3'
]
midfielder_stats = [
    'Passes completed', 'Progressive passes', 'Passes into final third', 'Shot creating actions',
    'Interceptions', 'Balls blocked', 'Expected Assisted Goals', 'Carries into final 1/3',
    'Goals', 'Touches', 'Long passes completed %', 'Clearances'
]
defender_stats = [
    'Tackles won %', 'Clearances', 'Interceptions', 'Progressive moved ball distance', 'Progressive passes',
    'Aerial duels won %', 'Balls blocked', 'Recoveries', 'Passes attempted', 'Errors', 'Fouls committed', 'Progressive pass distance', 'Yellow cards'
]

# Visualisierung 3: Transfers Analysis
def categorize_age(age):
    if age < 25:
        return 'Under 25'
    elif 25 <= age <= 30:
        return '25-30'
    else:
        return 'Over 30'
transfers_df['Age Group'] = transfers_df['Age'].apply(categorize_age)
colors = {'DF': 'green', 'MF': 'blue', 'FW': 'red'}

# Visualisierung 4: Club Transfer Details
transfer_details_df['Fee'] = pd.to_numeric(transfer_details_df['Fee'], errors='coerce').fillna(0)
big6_clubs = ['Liverpool', 'Manchester United', 'Manchester City', 'Chelsea', 'Arsenal', 'Tottenham Hotspur']
df_big6 = transfer_details_df[transfer_details_df['Club'].isin(big6_clubs)]
seasons = sorted(df_big6['Season'].unique())

# Visualisierung 5: Club Home & Away Performance
club_results_df['Date'] = pd.to_datetime(club_results_df['Date'])
club_results_df['Points'] = club_results_df['Points'].astype(int)
home_points = club_results_df[club_results_df['Venue'] == 'Home'].groupby('Club')['Points'].mean().reset_index()
away_points = club_results_df[club_results_df['Venue'] == 'Away'].groupby('Club')['Points'].mean().reset_index()
points = pd.merge(home_points, away_points, on='Club', suffixes=('_Home', '_Away'))
points['Difference'] = points['Points_Home'] - points['Points_Away']
points = points.sort_values('Club')
logo_dir = './logos/'
placeholder_image = os.path.join(logo_dir, "Tottenham Hotspur.png")
placeholder_base64 = image_to_base64(placeholder_image)
club_logos = {}
for club in points['Club']:
    logo_path = os.path.join(logo_dir, f"{club}.png")
    if os.path.isfile(logo_path):
        club_logos[club] = image_to_base64(logo_path)
    else:
        club_logos[club] = placeholder_base64

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Football Analysis Dashboard"

# Define the layout of the app
app.layout = dbc.Container([
    html.H1("Football Analysis Dashboard", className="text-center text-light my-4"),

    dbc.Tabs([
        dbc.Tab(label="Top Scorers", tab_id="top-scorers-tab"),
        dbc.Tab(label="Player Radar Charts", tab_id="player-radar-charts-tab"),
        dbc.Tab(label="Transfers Analysis", tab_id="transfers-analysis-tab"),
        dbc.Tab(label="Club Transfer Details", tab_id="club-transfer-details-tab"),
        dbc.Tab(label="Home & Away Performance", tab_id="home-away-performance-tab"),
    ], id="tabs", active_tab="top-scorers-tab"),

    html.Div(id="tab-content")
], fluid=True)

# Callback to render tab content
@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab")]
)
def render_tab_content(active_tab):
    if active_tab == "top-scorers-tab":
        return html.Div([
            dcc.Graph(id='top-scorers-graph', style={'height': '1000px', 'position': 'relative'}),
            dcc.Slider(
                id='matchday-slider',
                min=agg_df['MatchDay'].min(),
                max=agg_df['MatchDay'].max(),
                value=agg_df['MatchDay'].min(),
                marks={str(day): str(day) for day in agg_df['MatchDay'].unique()},
                step=None
            ),
            html.Div([
                html.Button('Start Animation', id='start-button', n_clicks=0, style={'margin-right': '10px'}),
                html.Button('Pause Animation', id='pause-button', n_clicks=0, style={'margin-right': '10px'}),
                html.Button('Restart Animation', id='restart-button', n_clicks=0),
            ], style={'position': 'relative', 'zIndex': '1'}),
            dcc.Interval(
                id='interval-component',
                interval=1000,  # 1000 milliseconds = 1 second
                n_intervals=0,
                disabled=True
            ),
        ])
    elif active_tab == "player-radar-charts-tab":
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H3("Select Attacking Players", style={'color': 'orange'}),
                    dcc.Dropdown(
                        id='attacker-dropdown',
                        options=[{'label': f"{player} ({club}, {age}, {nation})", 'value': player}
                                 for player, club, age, nation in zip(players_df[players_df['Position'] == 'FW']['Player'],
                                                                      players_df[players_df['Position'] == 'FW']['Club'],
                                                                      players_df[players_df['Position'] == 'FW']['Age'],
                                                                      players_df[players_df['Position'] == 'FW']['Nation'])],
                        multi=True,
                        placeholder="Select attacking players",
                        style={'backgroundColor': 'black', 'color': 'orange'}
                    ),
                    dcc.Graph(id='attacker-radar-chart', figure=create_empty_radar_chart()),
                    dash_table.DataTable(
                        id='attacker-table',
                        style_table={'overflowX': 'auto', 'whiteSpace': 'normal'},
                        style_cell={'textAlign': 'left', 'backgroundColor': 'black', 'color': 'orange'},
                        style_header={'backgroundColor': 'black', 'color': 'orange'}
                    )
                ], width=12)
            ]),
            dbc.Row([
                dbc.Col([
                    html.H3("Select Midfield Players", style={'color': 'orange'}),
                    dcc.Dropdown(
                        id='midfielder-dropdown',
                        options=[{'label': f"{player} ({club}, {age}, {nation})", 'value': player}
                                 for player, club, age, nation in zip(players_df[players_df['Position'] == 'MF']['Player'],
                                                                      players_df[players_df['Position'] == 'MF']['Club'],
                                                                      players_df[players_df['Position'] == 'MF']['Age'],
                                                                      players_df[players_df['Position'] == 'MF']['Nation'])],
                        multi=True,
                        placeholder="Select midfield players",
                        style={'backgroundColor': 'black', 'color': 'orange'}
                    ),
                    dcc.Graph(id='midfielder-radar-chart', figure=create_empty_radar_chart()),
                    dash_table.DataTable(
                        id='midfielder-table',
                        style_table={'overflowX': 'auto', 'whiteSpace': 'normal'},
                        style_cell={'textAlign': 'left', 'backgroundColor': 'black', 'color': 'orange'},
                        style_header={'backgroundColor': 'black', 'color': 'orange'}
                    )
                ], width=12)
            ]),
            dbc.Row([
                dbc.Col([
                    html.H3("Select Defensive Players", style={'color': 'orange'}),
                    dcc.Dropdown(
                        id='defender-dropdown',
                        options=[{'label': f"{player} ({club}, {age}, {nation})", 'value': player}
                                 for player, club, age, nation in zip(players_df[players_df['Position'] == 'DF']['Player'],
                                                                      players_df[players_df['Position'] == 'DF']['Club'],
                                                                      players_df[players_df['Position'] == 'DF']['Age'],
                                                                      players_df[players_df['Position'] == 'DF']['Nation'])],
                        multi=True,
                        placeholder="Select defensive players",
                        style={'backgroundColor': 'black', 'color': 'orange'}
                    ),
                    dcc.Graph(id='defender-radar-chart', figure=create_empty_radar_chart()),
                    dash_table.DataTable(
                        id='defender-table',
                        style_table={'overflowX': 'auto', 'whiteSpace': 'normal'},
                        style_cell={'textAlign': 'left', 'backgroundColor': 'black', 'color': 'orange'},
                        style_header={'backgroundColor': 'black', 'color': 'orange'}
                    )
                ], width=12)
            ])
        ])
    elif active_tab == "transfers-analysis-tab":
        return html.Div([
            html.H1("Player Transfers Analysis", style={'color': 'orange'}),
            dcc.Dropdown(
                id='club-dropdown',
                options=[{'label': club, 'value': club} for club in transfers_df['Club'].unique()] + [{'label': 'All', 'value': 'All'}],
                value='All',
                multi=False,
                placeholder='Select a club',
                style={'backgroundColor': 'black', 'color': 'orange'}
            ),
            dcc.Dropdown(
                id='position-dropdown',
                options=[{'label': pos, 'value': pos} for pos in transfers_df['Position'].unique() if pd.notna(pos)] + [{'label': 'All', 'value': 'All'}],
                value='All',
                multi=False,
                placeholder='Select a position',
                style={'backgroundColor': 'black', 'color': 'orange'}
            ),
            dcc.Graph(id='scatter-plot')
        ], style={'backgroundColor': 'black'})
    elif active_tab == "club-transfer-details-tab":
        return html.Div([
            html.H1("Big 6 Club Transfer Incomes and Expenses", className="text-center text-light my-4"),
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
    elif active_tab == "home-away-performance-tab":
        return html.Div([
            html.H1("Premier League Home & Away Performance"),
            html.Label("Sort by difference:"),
            dcc.Dropdown(
                id='sort-dropdown',
                options=[
                    {'label': 'Ascending', 'value': 'asc'},
                    {'label': 'Descending', 'value': 'desc'}
                ],
                value=None,
                clearable=True
            ),
            dcc.Graph(id='performance-graph')
        ])

# Callback functions for interactive updates
@app.callback(
    [Output('top-scorers-graph', 'figure'),
     Output('interval-component', 'disabled'),
     Output('interval-component', 'n_intervals'),
     Output('matchday-slider', 'value')],
    [Input('start-button', 'n_clicks'),
     Input('pause-button', 'n_clicks'),
     Input('restart-button', 'n_clicks'),
     Input('interval-component', 'n_intervals'),
     Input('matchday-slider', 'value')],
    [State('interval-component', 'disabled'),
     State('interval-component', 'n_intervals')]
)
def update_output(start_n_clicks, pause_n_clicks, restart_n_clicks, n_intervals, slider_value, interval_disabled, current_intervals):
    ctx = dash.callback_context

    if not ctx.triggered:
        return dash.no_update, interval_disabled, dash.no_update, slider_value

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'start-button':
        return dash.no_update, False, slider_value - agg_df['MatchDay'].min(), slider_value

    if trigger_id == 'pause-button':
        return dash.no_update, True, current_intervals, slider_value

    if trigger_id == 'restart-button':
        return dash.no_update, False, 0, agg_df['MatchDay'].min()

    if trigger_id == 'matchday-slider':
        selected_day = slider_value
        fig = update_figure(selected_day)
        return fig, True, n_intervals, selected_day

    selected_day = agg_df['MatchDay'].min() + n_intervals
    if selected_day > agg_df['MatchDay'].max():
        return dash.no_update, True, n_intervals, slider_value

    fig = update_figure(selected_day)
    return fig, True if trigger_id == 'matchday-slider' else interval_disabled, n_intervals, selected_day

def update_figure(selected_day):
    filtered_df = agg_df[agg_df['MatchDay'] <= selected_day]
    cumulative_goals = filtered_df.groupby(['Player', 'Squad'])['Cumulative Goals'].max().reset_index()
    cumulative_goals = cumulative_goals.set_index('Player').reindex(top_10_players).reset_index()
    cumulative_goals['Cumulative Goals'].fillna(0, inplace=True)
    cumulative_goals['Player'] = pd.Categorical(cumulative_goals['Player'], categories=top_10_players, ordered=True)
    cumulative_goals = cumulative_goals.sort_values('Player')
    cumulative_goals['Color'] = cumulative_goals['Squad'].map(squad_colors)

    fig = go.Figure(go.Bar(
        x=cumulative_goals['Cumulative Goals'],
        y=cumulative_goals['Player'],
        orientation='h',
        text=[f"{player}: {goals} ({squad})" for player, goals, squad in zip(cumulative_goals['Player'], cumulative_goals['Cumulative Goals'], cumulative_goals['Squad'])],
        marker=dict(color=cumulative_goals['Color']),
        textposition='inside',
        textfont=dict(size=26, color="black")
    ))
    
    fig.update_layout(
        title=f'Top 10 Scorers up to MatchDay {selected_day}',
        yaxis={'categoryorder': 'total ascending'},
        height=1000,
        margin=dict(l=200, r=20, t=40, b=40),
        xaxis={'range': [0, 25]},
        yaxis_title=None,
        transition={'duration': 1000, 'easing': 'cubic-in-out'},
        yaxis_visible=False
    )
    fig.add_annotation(
        text=f"MATCHDAY {selected_day}",
        xref="paper", yref="paper",
        x=0.95, y=0.05,
        font=dict(size=30, color="Grey"),
        showarrow=False,
        opacity=0.8
    )

    return fig

def create_empty_radar_chart():
    fig = go.Figure()
    fig.update_layout(
        template='plotly_dark',
        polar=dict(
            radialaxis=dict(
                visible=False,
                range=[0, 100]
            ),
            angularaxis=dict(
                visible=True
            )
        ),
        showlegend=False
    )
    return fig

def create_horizontal_table(players_stats, stats):
    data = {'Statistic per 90': ['Player', 'Club', 'Age', 'Minutes played'] + stats}
    for player_stats in players_stats:
        data[player_stats['Player']] = [
            player_stats['Player'], player_stats['Club'], player_stats['Age'], player_stats['Minutes played']
        ] + [round(player_stats[stat], 2) for stat in stats]
    return pd.DataFrame(data).to_dict('records')

@app.callback(
    [Output('attacker-radar-chart', 'figure'),
     Output('attacker-table', 'data'),
     Output('attacker-table', 'columns')],
    [Input('attacker-dropdown', 'value')]
)
def update_attacker_chart(selected_players):
    if not selected_players:
        return create_empty_radar_chart(), [], []

    fig = go.Figure()
    players_stats = []

    for player in selected_players:
        player_data = players_df[players_df['Player'] == player].iloc[0]
        stats = [category + '_percentile' for category in attacker_stats]
        fig.add_trace(go.Scatterpolar(
            r=[player_data[stat] for stat in stats] + [player_data[stats[0]]],
            theta=[stat.replace('_percentile', '') for stat in stats] + [stats[0].replace('_percentile', '')],
            fill='toself',
            name=player,
            hovertemplate=f'<b>{player}</b><br>%{{theta}}: Better than %{{r:.0f}}%'
        ))
        player_stats = players_df[players_df['Player'] == player][attacker_stats + ['Player', 'Club', 'Age', 'Minutes played']].to_dict('records')[0]
        players_stats.append(player_stats)

    fig.update_layout(
        template='plotly_dark',
        polar=dict(
            radialaxis=dict(
                visible=False,
                range=[0, 100]
            ),
            angularaxis=dict(
                visible=True
            )
        ),
        showlegend=True
    )

    table_data = create_horizontal_table(players_stats, attacker_stats)
    columns = [{"name": "Statistic per 90", "id": "Statistic per 90"}] + [{"name": player, "id": player} for player in selected_players]
    
    return fig, table_data, columns

@app.callback(
    [Output('midfielder-radar-chart', 'figure'),
     Output('midfielder-table', 'data'),
     Output('midfielder-table', 'columns')],
    [Input('midfielder-dropdown', 'value')]
)
def update_midfielder_chart(selected_players):
    if not selected_players:
        return create_empty_radar_chart(), [], []

    fig = go.Figure()
    players_stats = []

    for player in selected_players:
        player_data = players_df[players_df['Player'] == player].iloc[0]
        stats = [category + '_percentile' for category in midfielder_stats]
        fig.add_trace(go.Scatterpolar(
            r=[player_data[stat] for stat in stats] + [player_data[stats[0]]],
            theta=[stat.replace('_percentile', '') for stat in stats] + [stats[0].replace('_percentile', '')],
            fill='toself',
            name=player,
            hovertemplate=f'<b>{player}</b><br>%{{theta}}: Better than %{{r:.0f}}%'
        ))
        player_stats = players_df[players_df['Player'] == player][midfielder_stats + ['Player', 'Club', 'Age', 'Minutes played']].to_dict('records')[0]
        players_stats.append(player_stats)

    fig.update_layout(
        template='plotly_dark',
        polar=dict(
            radialaxis=dict(
                visible=False,
                range=[0, 100]
            ),
            angularaxis=dict(
                visible=True
            )
        ),
        showlegend=True
    )

    table_data = create_horizontal_table(players_stats, midfielder_stats)
    columns = [{"name": "Statistic per 90", "id": "Statistic per 90"}] + [{"name": player, "id": player} for player in selected_players]
    
    return fig, table_data, columns

@app.callback(
    [Output('defender-radar-chart', 'figure'),
     Output('defender-table', 'data'),
     Output('defender-table', 'columns')],
    [Input('defender-dropdown', 'value')]
)
def update_defender_chart(selected_players):
    if not selected_players:
        return create_empty_radar_chart(), [], []

    fig = go.Figure()
    players_stats = []

    for player in selected_players:
        player_data = players_df[players_df['Player'] == player].iloc[0]
        stats = [category + '_percentile' for category in defender_stats]
        fig.add_trace(go.Scatterpolar(
            r=[player_data[stat] for stat in stats] + [player_data[stats[0]]],
            theta=[stat.replace('_percentile', '') for stat in stats] + [stats[0].replace('_percentile', '')],
            fill='toself',
            name=player,
            hovertemplate=f'<b>{player}</b><br>%{{theta}}: Better than %{{r:.0f}}%'
        ))
        player_stats = players_df[players_df['Player'] == player][defender_stats + ['Player', 'Club', 'Age', 'Minutes played']].to_dict('records')[0]
        players_stats.append(player_stats)

    fig.update_layout(
        template='plotly_dark',
        polar=dict(
            radialaxis=dict(
                visible=False,
                range=[0, 100]
            ),
            angularaxis=dict(
                visible=True
            )
        ),
        showlegend=True
    )

    table_data = create_horizontal_table(players_stats, defender_stats)
    columns = [{"name": "Statistic per 90", "id": "Statistic per 90"}] + [{"name": player, "id": player} for player in selected_players]
    
    return fig, table_data, columns

def add_trendline(fig, df, position, color):
    df_position = df[df['Position'] == position]
    if len(df_position) > 1:
        z = np.polyfit(df_position['Fee'], df_position['Total Score'], 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=df_position['Fee'],
            y=p(df_position['Fee']),
            mode='lines',
            name=f'Trendline {position}',
            line=dict(color=color, width=3),
            showlegend=True
        ))

def add_age_line(fig, df):
    df_sorted = df.sort_values('Fee')
    z = np.polyfit(df_sorted['Fee'], df_sorted['Age'], 1)
    p = np.poly1d(z)
    fig.add_trace(go.Scatter(
        x=df_sorted['Fee'],
        y=p(df_sorted['Fee']),
        mode='lines',
        name='Average Age',
        line=dict(color='yellow', width=3),
        yaxis='y2',
        showlegend=True
    ))

@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('club-dropdown', 'value'),
     Input('position-dropdown', 'value')]
)
def update_scatter_plot(selected_club, selected_position):
    filtered_df = transfers_df

    if selected_club != 'All':
        filtered_df = filtered_df[filtered_df['Club'] == selected_club]
    
    if selected_position != 'All':
        filtered_df = filtered_df[filtered_df['Position'] == selected_position]

    scatter_fig = px.scatter(
        filtered_df,
        x='Fee',
        y='Total Score',
        color='Position',
        color_discrete_map=colors,
        hover_data={'Player': True, 'Age': True, 'Fee': True, 'Total Score': True, 'Club': True, 'Position': True},
        title="Scatter Plot of Fee vs. Total Score",
        labels={'Fee': 'Transfer Fee (€m)', 'Total Score': 'Total Score'},
        template='plotly_dark'
    )

    scatter_fig.update_traces(marker=dict(size=14, opacity=0.8))
    scatter_fig.update_layout(
        height=1600,
        xaxis_title='Transfer Fee (€m)',
        yaxis_title='Total Score',
        title={
            'text': "Scatter Plot of Fee vs. Total Score",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        legend_title_text='Position',
        font=dict(color='orange'),
        yaxis2=dict(
            title='Average Age',
            overlaying='y',
            side='right',
            showgrid=False,
            range=[18, 35]
        )
    )

    for position, color in colors.items():
        add_trendline(scatter_fig, filtered_df, position, color)

    add_age_line(scatter_fig, filtered_df)

    return scatter_fig

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

@app.callback(
    Output('performance-graph', 'figure'),
    [Input('sort-dropdown', 'value')]
)
def update_graph(sort_order):
    if sort_order:
        sorted_points = points.sort_values('Difference', ascending=(sort_order == 'asc'))
    else:
        sorted_points = points

    fig = go.Figure()

    for i in range(len(sorted_points)):
        fig.add_trace(go.Scatter(
            x=[sorted_points['Club'].iloc[i], sorted_points['Club'].iloc[i]], 
            y=[sorted_points['Points_Home'].iloc[i], sorted_points['Points_Away'].iloc[i]],
            mode='lines',
            line=dict(color='gray', width=2),
            showlegend=False
        ))

    for club in sorted_points['Club']:
        home_y = sorted_points[sorted_points['Club'] == club]['Points_Home'].values[0]
        away_y = sorted_points[sorted_points['Club'] == club]['Points_Away'].values[0]

        fig.add_layout_image(
            dict(
                source=club_logos[club],
                xref="x",
                yref="y",
                x=club,
                y=home_y,
                sizex=0.4,
                sizey=0.4,
                xanchor="center",
                yanchor="middle"
            )
        )
        fig.add_layout_image(
            dict(
                source=club_logos[club],
                xref="x",
                yref="y",
                x=club,
                y=away_y,
                sizex=0.2,
                sizey=0.2,
                xanchor="center",
                yanchor="middle"
            )
        )

    fig.add_trace(go.Scatter(
        x=sorted_points['Club'], 
        y=sorted_points['Points_Home'],
        mode='markers',
        marker=dict(size=0),
        hoverinfo='text',
        text=[f"Average points per home game for {club}: {round(val, 2)}" for club, val in zip(sorted_points['Club'], sorted_points['Points_Home'])]
    ))

    fig.add_trace(go.Scatter(
        x=sorted_points['Club'], 
        y=sorted_points['Points_Away'],
        mode='markers',
        marker=dict(size=0),
        hoverinfo='text',
        text=[f"Average points per away game for {club}: {round(val, 2)}" for club, val in zip(sorted_points['Club'], sorted_points['Points_Away'])]
    ))

    fig.update_layout(
        title="Average Points for Home and Away Games by Club",
        xaxis_title="Club",
        yaxis_title="Average Points",
        xaxis=dict(
            tickmode='array', 
            tickvals=sorted_points['Club'], 
            ticktext=sorted_points['Club'],
            range=[-1, len(sorted_points['Club'])]
        ),
        yaxis=dict(range=[0, max(sorted_points['Points_Home'].max(), sorted_points['Points_Away'].max()) + 1]),
        height=1000,
        margin=dict(l=100, r=100, t=100, b=100),
        showlegend=False
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
