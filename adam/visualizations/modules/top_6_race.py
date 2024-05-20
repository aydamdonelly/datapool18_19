import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output
import os
import base64

# Read data
df = pd.read_csv("../../adrian/data/pl_club_results.csv")

# Sort df based on 'Date' column
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values(by='Date')

# Create a new column that sorts the matchdays in their actual chronological order
df['Chronological Matchday'] = df.groupby('Club').cumcount() + 1

df['Accumulated Points'] = 0
df['Goal Difference'] = 0
df['League Position'] = 0

# Dictionary to store each club's current position and statistics
club_info = {}

# Calculate accumulated points and goal difference
for index, row in df.iterrows():
    club = row['Club']
    points = row['Points']
    ga = row['GA']
    gf = row['GF']
    matchday = row['Chronological Matchday']
    
    if club not in club_info:
        club_info[club] = {'Accumulated Points': 0, 'Goal Difference': 0}
    
    club_info[club]['Accumulated Points'] += points
    club_info[club]['Goal Difference'] += gf - ga
    
    df.at[index, 'Accumulated Points'] = club_info[club]['Accumulated Points']
    df.at[index, 'Goal Difference'] = club_info[club]['Goal Difference']

# Determine league position based on accumulated points and goal difference for each matchday
for matchday in range(1, 39):
    matchday_df = df[df['Chronological Matchday'] == matchday]
    sorted_clubs = matchday_df.sort_values(by=['Accumulated Points', 'Goal Difference'], ascending=[False, False])
    sorted_clubs['League Position'] = range(1, len(sorted_clubs) + 1)
    df.loc[sorted_clubs.index, 'League Position'] = sorted_clubs['League Position']

# Select only top 6 league positions each matchday
top_6_clubs_df = df[df['League Position'] <= 6]

# DataFrame to store whether each club is in the top 6 for each matchday
top_6_status = pd.DataFrame(index=range(1, 39), columns=top_6_clubs_df['Club'].unique())
for matchday in range(1, 39):
    matchday_data = top_6_clubs_df[top_6_clubs_df['Chronological Matchday'] == matchday]
    for club in top_6_clubs_df['Club'].unique():
        top_6_status.loc[matchday, club] = (club in matchday_data['Club'].values)

# Directory containing club logos
logo_dir = '../visualizations/logos' 

# Default placeholder image
placeholder_image = os.path.join(logo_dir, "Tottenham Hotspur.png")

# Mapping of club names to their base64 logo strings
club_logos = {}
for club in top_6_clubs_df['Club'].unique():
    logo_path = os.path.join(logo_dir, f"{club}.png")
    if os.path.isfile(logo_path):
        with open(logo_path, 'rb') as f:
            encoded_image = base64.b64encode(f.read()).decode('ascii')
        club_logos[club] = 'data:image/png;base64,{}'.format(encoded_image)
    else:
        print(f"Warning: Logo file for {club} not found. Using placeholder.")
        with open(placeholder_image, 'rb') as f:
            encoded_image = base64.b64encode(f.read()).decode('ascii')
        club_logos[club] = 'data:image/png;base64,{}'.format(encoded_image)

def create_figure():
    fig = go.Figure()

    for club in top_6_clubs_df['Club'].unique():
        x_values = []
        y_values = []
        hover_texts = []
        club_data = top_6_clubs_df[top_6_clubs_df['Club'] == club]
        
        for matchday in range(1, 39):
            if top_6_status.loc[matchday, club]:
                row = club_data[club_data['Chronological Matchday'] == matchday].iloc[0]
                x_values.append(row['Chronological Matchday'])
                y_values.append(row['League Position'])
                hover_texts.append(f"<b>{club}</b><br>Points: {row['Accumulated Points']}<br>Goal Difference: {row['Goal Difference']}")
                
                fig.add_layout_image(
                    dict(
                        source=club_logos[club],
                        xref="x",
                        yref="y",
                        x=row['Chronological Matchday'],
                        y=row['League Position'],
                        sizex=0.4,
                        sizey=0.4,
                        xanchor="center",
                        yanchor="middle"
                    )
                )
            else:
                x_values.append(None)
                y_values.append(None)
                hover_texts.append(None)

        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines+markers',
            name=club,
            line=dict(shape='spline', width=4),
            marker=dict(size=7),
            hoverinfo="text",
            hovertext=hover_texts,
            showlegend=False,
        ))

    fig.update_layout(
        title='The Race for The Top Spots',
        xaxis_title='Chronological Matchday',
        yaxis_title='League Position',
        legend_title='Club',
        yaxis=dict(range=[0.5, 6.5], autorange='reversed'),
        height=450,
        xaxis=dict(tickmode='linear', dtick='M1', range=[0.5, 38.5]),
        xaxis_rangeslider=dict(
            visible=True,
            thickness=0.02, 
            bgcolor='lightgrey',
            range=[0.5, 38.5],
        ),
        clickmode='none'
    )

    return fig

def layout():
    return html.Div([
        dcc.Graph(id='league-position-graph')
    ])

def register_callbacks(app):
    @app.callback(
        Output('league-position-graph', 'figure'),
        [Input('league-position-graph', 'hoverData')]
    )
    def update_graph(hover_data):
        return create_figure()
