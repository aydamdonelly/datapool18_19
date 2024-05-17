import pandas as pd
import plotly.express as px

# Load the data from a CSV file
df = pd.read_csv('../transfer_data.csv')

# Filter for the desired season
df = df[df['Season'] == '2018/2019']

# Convert 'Fee' to numeric, handling non-numeric data as NaN and then replacing NaN with 0
# Optionally convert 'Fee' into a formatted string if needed directly in the DataFrame
# df['Fee'] = df['Fee'].apply(lambda x: f"{x:.2f}M €")
df['Fee'] = pd.to_numeric(df['Fee'], errors='coerce').fillna(0)
# Create a bar plot
fig = px.bar(
    df,
    x='Team',
    y='Fee',
    color='Transfer',
    barmode='group',
    title='Club Transfer Details for 2018/2019 Season',
    labels={'Fee': 'Fee (in Million €)'},
    hover_data=["Fee", 'Player', 'Position']
)

# Customize the hover information
fig.update_traces(
    hovertemplate='<br>'.join([
        # customdata is used to pass additional data to the hover information, its obtained from the DataFrame columns you can see them with 
        'Player: %{customdata[0]}',
        'Position: %{customdata[1]}',
        "Fee: %{y:,.2f}M €"
    ])
)

#print each hover_data from fig

# Display the plot
fig.show()