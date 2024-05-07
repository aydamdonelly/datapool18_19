import pandas as pd
import plotly.graph_objects as go

# Assuming df is your DataFrame containing the data
# Assuming 'Points' and 'GA' (goals against) are in integer format
# Assuming 'Club' and 'Date' are in string format
df = pd.read_csv("adrian/pl_club_results.csv")

# Initialize new columns for accumulated points, goal difference, and league position
df['Accumulated Points'] = 0
df['Goal Difference'] = 0
df['League Position'] = 0

# Initialize dictionary to store each club's current position and statistics
club_info = {}

# First loop: Calculate accumulated points and goal difference
for index, row in df.iterrows():
    club = row['Club']
    points = row['Points']
    ga = row['GA']
    gf = row['GF']
    
    # Initialize club info if not already initialized
    if club not in club_info:
        club_info[club] = {'Accumulated Points': 0, 'Goal Difference': 0}
    
    # Update accumulated points and goal difference
    club_info[club]['Accumulated Points'] += points
    club_info[club]['Goal Difference'] += gf - ga
    
    # Update DataFrame with accumulated points and goal difference
    df.at[index, 'Accumulated Points'] = club_info[club]['Accumulated Points']
    df.at[index, 'Goal Difference'] = club_info[club]['Goal Difference']

# Second loop: Determine league position based on accumulated points and goal difference for each matchday
for matchday in range(1, 39):
    # Filter DataFrame for the current matchday
    matchday_df = df[df['Round'] == f'Matchweek {matchday}']
    
    # Sort clubs by accumulated points and goal difference for this matchday
    sorted_clubs = matchday_df.sort_values(by=['Accumulated Points', 'Goal Difference'], ascending=[False, False])

    
    # Assign league position based on sorted order
    sorted_clubs['League Position'] = range(1, len(sorted_clubs) + 1)
    
    # Update DataFrame with league position for this matchday
    df.loc[sorted_clubs.index, 'League Position'] = sorted_clubs['League Position']

# Create a line chart using Plotly
fig = go.Figure()

# Add a line for each club
for club in df['Club'].unique():
    club_data = df[df['Club'] == club]
    fig.add_trace(go.Scatter(x=club_data['Round'], y=club_data['League Position'], mode='lines', name=club))

# Update layout
fig.update_layout(title='League Position Over the 2018/2019 Season',
                  xaxis_title='Matchday',
                  yaxis_title='League Position',
                  legend_title='Club')

# Show plot
fig.show()

# TODO: entweder doch nach datum sortieren oder nach Matchday (aktuell Reihenfolge falsch)