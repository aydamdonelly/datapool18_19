import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output
import os
import base64

# Load and preprocess the CSV data
file_path = '../data/pl_club_results.csv'
data = pd.read_csv(file_path)

# Ensure the data is in the correct format
data['Date'] = pd.to_datetime(data['Date'])
data['Points'] = data['Points'].astype(int)

# Calculate average points for home and away games for each club
home_points = data[data['Venue'] == 'Home'].groupby('Club')['Points'].mean().reset_index()
away_points = data[data['Venue'] == 'Away'].groupby('Club')['Points'].mean().reset_index()

# Merge the home and away points
points = pd.merge(home_points, away_points, on='Club', suffixes=('_Home', '_Away'))

# Calculate the difference in average points between home and away
points['Difference'] = points['Points_Home'] - points['Points_Away']

# Sort clubs alphabetically initially
points = points.sort_values('Club')

# Directory containing club logos
logo_dir = './logos/'

# Function to convert images to base64 strings
def image_to_base64(image_path):
    with open(image_path, 'rb') as f:
        encoded_image = base64.b64encode(f.read()).decode('ascii')
    return 'data:image/png;base64,{}'.format(encoded_image)

# Default placeholder image
placeholder_image = os.path.join(logo_dir, "Tottenham Hotspur.png")
placeholder_base64 = image_to_base64(placeholder_image)

# Mapping of club names to their base64 logo strings
club_logos = {}
for club in points['Club']:
    logo_path = os.path.join(logo_dir, f"{club}.png")
    if os.path.isfile(logo_path):
        club_logos[club] = image_to_base64(logo_path)
    else:
        print(f"Warning: Logo file for {club} not found. Using placeholder.")
        club_logos[club] = placeholder_base64

def layout():
    return html.Div([
        html.H1("Premier League Home & Away Performances", style={'textAlign': 'center', 'fontWeight': 'bold'}),
        html.Label("Difference indicates how much better or worse a team performs at home compared to away."),
        html.Label("Sort by difference (Ascending -> weakest home advantage to strongest and vice versa):"),
        dcc.Dropdown(
            id='sort-dropdown',
            options=[
                {'label': 'Ascending (lowest home advantage to highest)', 'value': 'asc'},
                {'label': 'Descending (highest home advantage to lowest)', 'value': 'desc'}
            ],
            value=None,
            clearable=True
        ),
        dcc.Graph(id='performance-graph'),
        html.Div([
            html.Span("Legend: ", style={'fontSize': '16px', 'fontWeight': 'bold'}),
            html.Img(src=club_logos['Liverpool'], style={'width': '60px', 'height': '60px'}),
            html.Span(" Home Performance ", style={'fontSize': '16px'}),
            html.Img(src=club_logos['Liverpool'], style={'width': '40px', 'height': '40px'}),
            html.Span(" Away Performance", style={'fontSize': '16px'}),
        ], style={'textAlign': 'center', 'marginTop': '10px'})
    ])

def register_callbacks(app):
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

        # Plotting the Difference in Home and Away Points
        for i in range(len(sorted_points)):
            fig.add_trace(go.Scatter(
                x=[sorted_points['Club'].iloc[i], sorted_points['Club'].iloc[i]], 
                y=[sorted_points['Points_Home'].iloc[i], sorted_points['Points_Away'].iloc[i]],
                mode='lines',
                line=dict(color='gray', width=2),
                showlegend=False
            ))

        # Adding Club Logos to the Plot
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
                    sizex=0.75,
                    sizey=0.75,
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
                    sizex=0.45,
                    sizey=0.45,
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

        # Updating the Layout
        fig.update_layout(
            xaxis_title="Club",
            yaxis_title="Average Points",
            xaxis=dict(
                tickmode='array', 
                tickvals=sorted_points['Club'], 
                ticktext=sorted_points['Club'],
                range=[-1, len(sorted_points['Club'])],
                title_font=dict(size=20, family='Arial, sans-serif', weight='bold'),
                tickfont=dict(size=16, family='Arial, sans-serif', weight='bold'),
                title_standoff=20  # Adjust the position of the x-axis title
            ),
            yaxis=dict(
                range=[0, 3.3],
                title_font=dict(size=45, family='Arial, sans-serif', weight='bold'),
                tickfont=dict(size=26, family='Arial, sans-serif', weight='bold'),
                showline=True,
                linewidth=2,
                linecolor='black'
            ),
            height=600,  # Decreased height for the chart
            margin=dict(l=100, r=100, t=20, b=100), 
            showlegend=False,
            font=dict(size=16, family='Arial, sans-serif')
        )

        return fig
