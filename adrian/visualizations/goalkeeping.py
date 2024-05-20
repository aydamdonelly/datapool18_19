import pandas as pd
import plotly.graph_objects as go
import os
import base64

df = pd.read_csv("adrian/data/goalkeeping_stats_pl.csv")
df_2 = pd.read_csv("adrian/data/t5_leagues_players_standard.csv")

# group by "Club" and aggregate the values we need for the scatter plot
agg_df = df.groupby('Club').agg({'GA': 'sum', 'Save%': 'mean', 'CS': 'sum'}).reset_index()

# color mapping for each club
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

# filter df_2 for PL keepers
pl_goalkeepers_df = df_2[df_2['Club'].isin(squad_colors.keys())]
pl_goalkeepers_df = pl_goalkeepers_df[pl_goalkeepers_df['Pos'] == 'GK']

# find first team keeper of each club (most matches played)
main_goalkeepers = pl_goalkeepers_df.groupby('Club')['MP'].idxmax()
main_goalkeepers_df = pl_goalkeepers_df.loc[main_goalkeepers]

main_goalkeepers_games_df = main_goalkeepers_df.groupby('Club').agg({'Player': 'first'}).reset_index()
main_goalkeepers_games_df.rename(columns={'Player': 'Main Goalkeeper'}, inplace=True)

# merge with aggregated goalkeeping stats
agg_df = pd.merge(agg_df, main_goalkeepers_games_df, on='Club')

### image implementation ###
logo_dir = 'adam/visualizations/logos' 

club_logos = {}
for club in agg_df['Club'].unique():
    logo_path = os.path.join(logo_dir, f"{club}.png")
    if os.path.isfile(logo_path):
        with open(logo_path, 'rb') as f:
            encoded_image = base64.b64encode(f.read()).decode('ascii')
        club_logos[club] = 'data:image/png;base64,{}'.format(encoded_image)
    else:
        print(f"Warning: Logo file for {club} not found. Using placeholder.")

### PLOTTING ####################################################

fig = go.Figure()

# trace for scatter points
for i, row in agg_df.iterrows():
    # custom hover data
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

# trace for images
for i, row in agg_df.iterrows():
    # image for respective data point / club
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

# annotation for bubble size explanation
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
    yaxis=dict(fixedrange=True), 
)

fig.show()











