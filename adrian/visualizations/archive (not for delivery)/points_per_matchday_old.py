import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html
from PIL import Image
import numpy as np

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

####### Plotting ###########################################################################

fig = go.Figure()

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
    
    # add the trace with the data
    fig.add_trace(go.Scatter(
        x=x_values,
        y=y_values,
        mode='lines+markers',
        name=club,
        line=dict(shape='spline'),
        marker=dict(size=7),
        hoverinfo="text",
        hovertext=hover_texts,
        hoverlabel=dict(
            font=dict(color="black")  
        )
    ))

fig.add_layout_image(
    dict(
    source = Image.open("adrian/res/club_badges/Premier_League-Logo.wine.png"),
    x = 1,
    y = 0.95,
    sizex=0.4,
    sizey=0.4,
    xanchor="right",
    yanchor="bottom",
    opacity=1,
    layer="above"
    ) 
)

fig.update_layout(
    title='The Race for The Top Spots',
    xaxis_title='Chronological Matchday',
    yaxis_title='League Position',
    legend_title='Club',
    yaxis=dict(autorange='reversed'), 
    height=450,
    xaxis=dict(tickmode='linear', dtick='M1', range = [0.5,38.5]),
    xaxis_rangeslider=dict( 
        visible=True,
        thickness=0.02, 
        bgcolor='lightgrey',
        range = [0.5,38.5],
    )
)

fig.show()

# app = Dash()
# app.layout = html.Div([
#     dcc.Graph(figure=fig),
# ])

# # app.run_server(debug=True)
# if __name__ == '__main__':
#     app.run_server(debug=True)