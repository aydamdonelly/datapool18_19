# goalkeeping_performance.py

import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output
import dash
import dash_bootstrap_components as dbc
import os
import base64

# Load the data
df = pd.read_csv("../../adrian/data/goalkeeping_stats_pl.csv")
df_2 = pd.read_csv("../../adrian/data/t5_leagues_players_standard.csv")

# Group by "Club" and aggregate the values we need for the scatter plot
agg_df = df.groupby('Club').agg({'GA': 'sum', 'Save%': 'mean', 'CS': 'sum'}).reset_index()

# Color mapping for each club
squad_colors = {
    'Arsenal': '#EF0107',
    'Bournemouth': '#D71920',
    'Brighton and Hove Albion': '#0057B8',
    'Burnley': '#6C1D45',
    'Cardiff City': '#0070B5',
    'Chelsea': '#034694',
    'Crystal Palace': '#1B458F',
    'Everton': '#003399',
    'Fulham': '#FFFFFF',
    'Huddersfield Town': '#0E63AD',
    'Leicester City': '#003090',
    'Liverpool': '#C8102E',
    'Manchester City': '#6CABDD',
    'Manchester United': '#DA291C',
    'Newcastle United': '#241F20',
    'Southampton': '#D71920',
    'Tottenham Hotspur': '#D3D3D3',
    'Watford': '#FBEC5D',
    'West Ham United': '#7C2C3B',
    'Wolverhampton Wanderers': '#FDB913'
}

# Filter df_2 for PL keepers
pl_goalkeepers_df = df_2[df_2['Club'].isin(squad_colors.keys())]
pl_goalkeepers_df = pl_goalkeepers_df[pl_goalkeepers_df['Pos'] == 'GK']

# Find first team keeper of each club (most matches played)
main_goalkeepers = pl_goalkeepers_df.groupby('Club')['MP'].idxmax()
main_goalkeepers_df = pl_goalkeepers_df.loc[main_goalkeepers]

main_goalkeepers_games_df = main_goalkeepers_df.groupby('Club').agg({'Player': 'first'}).reset_index()
main_goalkeepers_games_df.rename(columns={'Player': 'Main Goalkeeper'}, inplace=True)

# Merge with aggregated goalkeeping stats
agg_df = pd.merge(agg_df, main_goalkeepers_games_df, on='Club')

# Image implementation
logo_dir = '../visualizations/logos'

club_logos = {}
for club in agg_df['Club'].unique():
    logo_path = os.path.join(logo_dir, f"{club}.png")
    if os.path.isfile(logo_path):
        with open(logo_path, 'rb') as f:
            encoded_image = base64.b64encode(f.read()).decode('ascii')
        club_logos[club] = 'data:image/png;base64,{}'.format(encoded_image)
    else:
        print(f"Warning: Logo file for {club} not found. Using placeholder.")
        club_logos[club] = 'data:image/png;base64,{}'.format(base64.b64encode(open(os.path.join(logo_dir, "placeholder.png"), 'rb').read()).decode('ascii'))

def layout():
    return html.Div([
        html.H1("Premier League Goalkeeping Performance"),
        dcc.Graph(id='goalkeeping-performance-graph')
    ])

def register_callbacks(app):
    @app.callback(
        Output('goalkeeping-performance-graph', 'figure'),
        [Input('goalkeeping-performance-graph', 'id')]
    )
    def update_graph(_):
        fig = go.Figure()

        # Trace for scatter points
        for i, row in agg_df.iterrows():
            # Custom hover data
            hover_text = f"Club: {row['Club']}<br>Goals conceded: {row['GA']}<br>Save%: {row['Save%']:.2f}<br>Clean Sheets: {row['CS']}<br>Main Goalkeeper: {row['Main Goalkeeper']}"
            fig.add_trace(go.Scatter(
                x=[row['GA']],
                y=[row['Save%']],
                mode='markers',
                marker=dict(size=row['CS'] * 5, line=dict(width=2, color='DarkSlateGrey'), color=squad_colors[row['Club']]),
                name=row['Club'],
                text=hover_text,
                hovertemplate=hover_text,
                hoverlabel=dict(font=dict(color='black'), namelength=0, bgcolor='white'),
                showlegend=False  # Don't show scatter legend
            ))

        # Trace for images
        for i, row in agg_df.iterrows():
            # Image for respective data point / club
            fig.add_layout_image(
                dict(
                    source=club_logos[row['Club']],
                    xref="x",
                    yref="y",
                    x=row['GA'],
                    y=row['Save%'] + row['CS'] * 0.08,
                    sizex=row['CS'] * 0.13,
                    sizey=row['CS'] * 0.13,
                    xanchor="center",
                    yanchor="middle"
                )
            )

        # Annotation for bubble size explanation
        fig.add_annotation(
            x=0.167,
            y=1.03,
            xref='paper',
            yref='paper',
            text='Bubble size represents number of Clean Sheets - The bigger, the more Clean Sheets',
            showarrow=False,
            font=dict(color='black', size=12),
            xanchor="center",
            yanchor="middle"
        )

        fig.update_layout(
            title='Goals Against vs. Average Save% for Premier League Teams',
            xaxis_title='Goals Against',
            yaxis_title='Average Save%',
            dragmode='pan',
            xaxis=dict(fixedrange=True),
            yaxis=dict(fixedrange=True, range=[0, 100]),  # Adjusted y-axis range
        )

        return fig
