# this file is the "prototype" for the shots_all_season.py visualization

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load the dataset
df = pd.read_csv("adrian/data/all_shots_CLandPL.csv")

# to make sure xG and PSxG columns are numeric
df['xG'] = pd.to_numeric(df['xG'], errors='coerce')
df['PSxG'] = pd.to_numeric(df['PSxG'], errors='coerce')

# filter for rows where the club is Liverpool and the player is Roberto Firmino
df_firmino = df[(df['Squad'] == 'Liverpool') & (df['Player'] == 'Roberto Firmino')]

# filter shots on target
df_firmino_on_target = df_firmino[df_firmino['Outcome'].isin(['Goal', 'Saved'])]

# sort ascendingly by PSxG
df_firmino_sorted = df_firmino_on_target.sort_values(by=['PSxG'], ascending=[True])

# reset index to get shot IDs for the sorted DataFrame
df_firmino_sorted.reset_index(drop=True, inplace=True)
df_firmino_sorted['Shot_ID'] = df_firmino_sorted.index

fig = make_subplots()

# add scatter traces for each shot
for index, row in df_firmino_sorted.iterrows():
    xg_value = row['xG']
    psxg_value = row['PSxG']
    shot_id = row['Shot_ID']
    outcome = row['Outcome']
    
    if outcome == 'Goal':
        outcome_color = 'green'
    elif outcome == 'Saved':
        outcome_color = 'red'
    
    # add the initial xG marker
    fig.add_trace(
        go.Scatter(
            x=[xg_value],
            y=[shot_id],
            mode='markers',
            marker=dict(size=10, color='blue', opacity=0.6),
            name=f'Shot {shot_id} xG',
            showlegend=False
        )
    )
    
    # add the PSxG marker and the line connecting xG to PSxG if PSxG is present
    if not pd.isna(psxg_value):
        fig.add_trace(
            go.Scatter(
                x=[psxg_value],
                y=[shot_id],
                mode='markers',
                marker=dict(size=10, color=outcome_color, opacity=0.6),
                name=f'Shot {shot_id} PSxG',
                showlegend=False
            )
        )
        # add line shape to connect xG to PSxG
        fig.add_shape(
            type="line",
            x0=xg_value, y0=shot_id,
            x1=psxg_value, y1=shot_id,
            line=dict(color="gray", width=2),
            opacity=0.7,
            xref="x", yref="y"
        )

# Update layout
fig.update_layout(
    title="xG and PSxG for Roberto Firmino's On-Target Shots",
    xaxis_title='Value',
    yaxis_title='Shot ID',
    template='plotly_white'
)

# Show the plot
fig.show()




































