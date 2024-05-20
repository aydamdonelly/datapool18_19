import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import os
import base64

# Read data
df = pd.read_csv("adrian/data/pl_club_results.csv")

# sort df based on 'Date' column
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values(by='Date')

# with the current order, catch-up games will mess up the order of the games they have been played in
# so we have to create another column that sorts the matchdays in their actual chronological order
df['Chronological Matchday'] = df.groupby('Club').cumcount() + 1

df['Accumulated Points'] = 0
df['Goal Difference'] = 0
df['League Position'] = 0

# dictionary to store each club's current position and statistics
club_info = {}

# calculate accumulated points and goal difference (and store them in new columns)
for index, row in df.iterrows():
    club = row['Club']
    points = row['Points']
    ga = row['GA']
    gf = row['GF']
    matchday = row['Chronological Matchday']
    
    if club not in club_info:
        club_info[club] = {'Accumulated Points': 0, 'Goal Difference': 0}
    
    # update accumulated points and goal difference
    club_info[club]['Accumulated Points'] += points
    club_info[club]['Goal Difference'] += gf - ga
    
    # update df with accumulated points and goal difference
    df.at[index, 'Accumulated Points'] = club_info[club]['Accumulated Points']
    df.at[index, 'Goal Difference'] = club_info[club]['Goal Difference']

# determine league position based on accumulated points and goal difference for each matchday
for matchday in range(1, 39):
    matchday_df = df[df['Chronological Matchday'] == matchday]
    sorted_clubs = matchday_df.sort_values(by=['Accumulated Points', 'Goal Difference'], ascending=[False, False])
    sorted_clubs['League Position'] = range(1, len(sorted_clubs) + 1)
    
    # update DataFrame with league position for this matchday
    df.loc[sorted_clubs.index, 'League Position'] = sorted_clubs['League Position']

# select only top 6 league positions each matchday
top_6_clubs_df = df[df['League Position'] <= 6]

# df to store whether each club is in the top 6 for each matchday
top_6_status = pd.DataFrame(index=range(1, 39), columns=top_6_clubs_df['Club'].unique())
# fill df with True/False depending on top6 or not
for matchday in range(1, 39):
    matchday_data = top_6_clubs_df[top_6_clubs_df['Chronological Matchday'] == matchday]
    for club in top_6_clubs_df['Club'].unique():
        top_6_status.loc[matchday, club] = (club in matchday_data['Club'].values)

for club in top_6_clubs_df['Club'].unique():
    club_data = top_6_clubs_df[top_6_clubs_df['Club'] == club]
    hover_text = club_data.apply(lambda row: f"<b>{club}</b><br>Points: {row['Accumulated Points']}<br>Goal Difference: {row['Goal Difference']}", axis=1)
    
    # lists to store x, y, and hover text values
    x_values = []
    y_values = []
    hover_texts = []
    
    # Iterate over each matchday and determine if the club is in the top 6
    # before this part existed, there was a mistake in the graphic
    # Bournemouth dropped out of the Top 6 after MD 5 and got in on MD 8 again
    # without this code, the datapoints from MD 5 and 8 would be connected, which implies they never dropped out
    for matchday in range(1, 39):
        if top_6_status.loc[matchday, club]:
            # If the club is in the top 6, add the data to the lists
            row = club_data[club_data['Chronological Matchday'] == matchday].iloc[0]
            x_values.append(row['Chronological Matchday'])
            y_values.append(row['League Position'])
            hover_texts.append(hover_text[row.name])
        else:
            # If the club is not in the top 6, add None values to create a break in the line
            x_values.append(None)
            y_values.append(None)
            hover_texts.append(None)

# Directory containing club logos
logo_dir = 'adam/visualizations/logos' 

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


# Initialize the Dash app
app = Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("The Race for The Top Spots"),
    dcc.Graph(id='league-position-graph')
])

# Define the callback to update the graph
@app.callback(
    Output('league-position-graph', 'figure'),
    [Input('league-position-graph', 'hoverData')]
)
def update_graph(hover_data):
    # Your plotting code here
    fig = go.Figure()

    # Loop through clubs and add traces
    for club in top_6_clubs_df['Club'].unique():
        x_values = []
        y_values = []
        hover_texts = []
        club_data = top_6_clubs_df[top_6_clubs_df['Club'] == club]
        
        # Iterate over each matchday and determine if the club is in the top 6
        for matchday in range(1, 39):
            if top_6_status.loc[matchday, club]:
                # If the club is in the top 6, add the data to the lists
                row = club_data[club_data['Chronological Matchday'] == matchday].iloc[0]
                x_values.append(row['Chronological Matchday'])
                y_values.append(row['League Position'])
                hover_texts.append(f"<b>{club}</b><br>Points: {row['Accumulated Points']}<br>Goal Difference: {row['Goal Difference']}")
                
                # Add image for this data point
                fig.add_layout_image(
                    dict(
                        source=club_logos[club],
                        xref="x",
                        yref="y",
                        x=row['Chronological Matchday'],  # Use the current matchday for x-coordinate
                        y=row['League Position'],  # Use the exact league position for y-coordinate
                        sizex=0.4,  # Adjust image size as needed
                        sizey=0.4,  # Adjust image size as needed
                        xanchor="center",
                        yanchor="middle"
                    )
                )
            else:
                # If the club is not in the top 6, add None values to create a break in the line
                x_values.append(None)
                y_values.append(None)
                hover_texts.append(None)

        # Add trace for the current club
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines+markers',
            name=club,
            line=dict(shape='spline', width=4),  # Increase line width
            marker=dict(size=7),
            hoverinfo="text",
            hovertext=hover_texts,
            showlegend=False,
        ))
        
    # Add layout
    fig.update_layout(
        title='The Race for The Top Spots',
        xaxis_title='Chronological Matchday',
        yaxis_title='League Position',
        legend_title='Club',
        yaxis=dict(range=[0.5, 6.5], autorange='reversed'),  # Limit y-axis to top 6 positions
        height=450,
        xaxis=dict(tickmode='linear', dtick='M1', range=[0.5, 38.5]),
        xaxis_rangeslider=dict(
            visible=True,
            thickness=0.02, 
            bgcolor='lightgrey',
            range=[0.5, 38.5],
        ),
        clickmode='none'  # Disable clicking to make lines disappear
    )



    return fig



# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)