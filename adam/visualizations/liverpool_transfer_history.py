import pandas as pd
import plotly.express as px

# Load the data from a CSV file
df = pd.read_csv('../transfer_data.csv')

# Convert 'Fee' to numeric, handling non-numeric data as NaN and then replacing NaN with 0
df['Fee'] = pd.to_numeric(df['Fee'], errors='coerce').fillna(0)

# Filter to include only Liverpool data
df_liverpool = df[df['Team'] == 'Liverpool']

# Pivot the data to sum fees by season and transfer type (Arrival, Departure)
seasonal_transfers = df_liverpool.groupby(['Season', 'Transfer']).agg({'Fee': 'sum'}).reset_index()

# Create a line plot
fig = px.line(
    seasonal_transfers,
    x='Season',
    y='Fee',
    color='Transfer',
    markers=True,  # Add markers to the line
    title='Liverpool Transfer Incomes and Expenses per Season',
    labels={'Fee': 'Total Fee (in Million €)'},
    category_orders={"Transfer": ["Arrival", "Departure"]}  # Ensure consistent color assignment
)

# Customize hover information
fig.update_traces(
    hovertemplate='<br>'.join([
        'Season: %{x}',
        'Transaction Type: %{data.name}',  # Here 'data.name' refers to the name of the trace, which is 'Transfer' type
        "Total Fee: %{y:,.2f}M €"
    ])
)

# Adjust layout options if needed
fig.update_layout(
    xaxis_title="Season",
    yaxis_title="Total Fee (in Million €)",
    xaxis={'type': 'category'}  # Treat the x-axis as categories (not continuous dates)
)

# Display the plot
fig.show()
