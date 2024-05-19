import pandas as pd
import plotly.graph_objects as go

# Load the CSV data
file_path = '../liverpool_shots_with_venue.csv'  # Update this to the correct path if needed
df = pd.read_csv(file_path)

# Convert 'Minute' to numeric
df['Minute'] = pd.to_numeric(df['Minute'], errors='coerce')

# Create a summary of shots per minute for home and away games
shots_per_minute_home = df[df['Venue'] == 'Home'].groupby('Minute').size()
shots_per_minute_away = df[df['Venue'] == 'Away'].groupby('Minute').size()

# Ensure all minutes from 1 to 90 are represented
minutes = range(1, 91)
shots_per_minute_home = shots_per_minute_home.reindex(minutes, fill_value=0)
shots_per_minute_away = shots_per_minute_away.reindex(minutes, fill_value=0)

# Create the figure
fig = go.Figure()

# Add Home shots
fig.add_trace(go.Bar(
    y=list(minutes),
    x=-shots_per_minute_home.values,  # Negative values for Home
    name='Home',
    orientation='h',
    marker=dict(color='blue'),
    width=0.8  # Make the bars narrower
))

# Add Away shots
fig.add_trace(go.Bar(
    y=list(minutes),
    x=shots_per_minute_away.values,
    name='Away',
    orientation='h',
    marker=dict(color='red'),
    width=0.8  # Make the bars narrower
))

# Update layout
fig.update_layout(
    title='Number of Shots Per Minute (Home vs Away)',
    barmode='relative',
    bargap=0.0,
    bargroupgap=0,
    xaxis=dict(
        title='Number of Shots',
        tickvals=[-10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10],
        ticktext=[10, 8, 6, 4, 2, 0, 2, 4, 6, 8, 10],
        range=[-10, 10]
    ),
    yaxis=dict(
        title='Minute',
        tickvals=list(minutes),
        ticktext=list(reversed(minutes)),  # Reverse the tick labels
        autorange='reversed',  # Invert y-axis to have minute 90 at the top
        tickmode='linear',
        tick0=1,
        dtick=1
    ),
    legend=dict(
        x=0.5,
        y=1.1,
        xanchor='center',
        orientation='h',
        font=dict(
            size=12,
        ),
        bgcolor='rgba(0,0,0,0)',
    ),
    plot_bgcolor='white',
    margin=dict(l=40, r=40, t=60, b=40),  # Adjust margins to make it more compact
    height=1200,  # Adjust height for better readability
    width=800  # Increase width for better readability of values
)

# Show the figure
fig.show()
