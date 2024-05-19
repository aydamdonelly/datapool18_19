    import pandas as pd
    import dash
    from dash import dcc, html
    from dash.dependencies import Input, Output
    import plotly.express as px
    import dash_bootstrap_components as dbc

    # Load the data from a CSV file
    df = pd.read_csv('../transfer_data.csv')

    # Convert 'Fee' to numeric, handling non-numeric data as NaN and then replacing NaN with 0
    df['Fee'] = pd.to_numeric(df['Fee'], errors='coerce').fillna(0)

    # Filter to include only Liverpool data
    df_liverpool = df[df['Club'] == 'Liverpool']

    # Group the data to sum fees by season and transfer type (Arrival, Departure)
    seasonal_transfers = df_liverpool.groupby(['Season', 'Transfer']).agg({'Fee': 'sum'}).reset_index()

    # Create a list of unique seasons
    seasons = sorted(df_liverpool['Season'].unique())

    # Initialize the Dash application
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

    # Layout of the Dash application
    app.layout = html.Div([
        html.H1("Liverpool Transfer Incomes and Expenses per Season", style={'color': 'orange'}),
        html.Label('Select Seasons:', style={'color': 'orange'}),
        dcc.RangeSlider(
            id='season-slider',
            min=0,
            max=len(seasons) - 1,
            value=[0, len(seasons) - 1],
            marks={i: season for i, season in enumerate(seasons)},
            step=1
        ),
        html.Label('Select Transfer Type:', style={'color': 'orange'}),
        dcc.Checklist(
            id='transfer-type-checklist',
            options=[
                {'label': 'Arrivals', 'value': 'Arrival'},
                {'label': 'Departures', 'value': 'Departure'}
            ],
            value=['Arrival', 'Departure'],
            inline=True,
            style={'color': 'orange'}
        ),
        dcc.Graph(id='line-plot')
    ], style={'backgroundColor': 'black', 'padding': '20px'})

    # Callback to update the plot based on selected seasons and transfer types
    @app.callback(
        Output('line-plot', 'figure'),
        [
            Input('season-slider', 'value'),
            Input('transfer-type-checklist', 'value')
        ]
    )
    def update_line_plot(selected_seasons, selected_transfer_types):
        filtered_df = seasonal_transfers[
            (seasonal_transfers['Season'].isin(seasons[selected_seasons[0]:selected_seasons[1] + 1])) &
            (seasonal_transfers['Transfer'].isin(selected_transfer_types))
        ]

        fig = px.line(
            filtered_df,
            x='Season',
            y='Fee',
            color='Transfer',
            markers=True,
            title='Liverpool Transfer Incomes and Expenses per Season',
            labels={'Fee': 'Total Fee (in Million €)'},
            category_orders={"Transfer": ["Arrival", "Departure"]}
        )

        # Customize hover information
        fig.update_traces(
            hovertemplate='<br>'.join([
                'Season: %{x}',
                'Transaction Type: %{data.name}',
                "Total Fee: %{y:,.2f}M €"
            ])
        )

        # Adjust layout options
        fig.update_layout(
            xaxis_title="Season",
            yaxis_title="Total Fee (in Million €)",
            xaxis={'type': 'category'},
            font=dict(color='orange'),
            plot_bgcolor='black',
            paper_bgcolor='black',
            legend_title_text='Transfer Type'
        )

        return fig

    # Run the Dash application
    if __name__ == '__main__':
        app.run_server(debug=True)
