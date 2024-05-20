import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# Import your modules
import modules.top_scorers as top_scorers
import modules.player_radar_charts as player_radar_charts
import modules.transfers_analysis as transfers_analysis
import modules.club_transfer_details as club_transfer_details
import modules.home_away_performance as home_away_performance
import modules.cl_results as cl_results
import modules.top_6_race as top_6_race
import modules.shot_analysis as shot_analysis
import modules.xg_difference as xg_difference
import modules.goalkeeping_performance as goalkeeping_performance  # Import the new module

# Initialize the Dash app with suppress_callback_exceptions=True
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "Liverpool 18/19 Season Analytical Dashboard"

# Define the layout of the app
app.layout = dbc.Container([
    html.H1("Liverpool 18/19 Season Analytical Dashboard", className="text-center my-4"),

    dbc.Tabs([
        dbc.Tab(label="Top 6 Race (Adrian)", tab_id="top-6-race-tab"),
        dbc.Tab(label="Top Scorers (Adam)", tab_id="top-scorers-tab"),
        dbc.Tab(label="Home & Away Performance (Adam)", tab_id="home-away-performance-tab"),
        dbc.Tab(label="xG Difference (Adrian)", tab_id="xg-difference-tab"),
        dbc.Tab(label="Shot Analysis (Adrian)", tab_id="shot-analysis-tab"),
        dbc.Tab(label="Goalkeeping Performance (Adrian)", tab_id="goalkeeping-performance-tab"),
        dbc.Tab(label="Player Radar Charts (Adam)", tab_id="player-radar-charts-tab"),
        dbc.Tab(label="CL Summary (Adrian)", tab_id="cl-results-tab"),
        dbc.Tab(label="Big 6 Transfers Analysis (Adam)", tab_id="transfers-analysis-tab"),
        dbc.Tab(label="Big 6 Transfer Comparison (Adam)", tab_id="club-transfer-details-tab"),
    ], id="tabs", active_tab="top-scorers-tab", className="custom-tabs"),

    html.Div(id="tab-content")
], fluid=True)

# Callback to render tab content
@app.callback(
    dash.dependencies.Output("tab-content", "children"),
    [dash.dependencies.Input("tabs", "active_tab")]
)
def render_tab_content(active_tab):
    if active_tab == "top-scorers-tab":
        return top_scorers.layout()
    elif active_tab == "player-radar-charts-tab":
        return player_radar_charts.layout()
    elif active_tab == "transfers-analysis-tab":
        return transfers_analysis.layout()
    elif active_tab == "club-transfer-details-tab":
        return club_transfer_details.layout()
    elif active_tab == "home-away-performance-tab":
        return home_away_performance.layout()
    elif active_tab == "cl-results-tab":
        return cl_results.layout()
    elif active_tab == "top-6-race-tab":
        return top_6_race.layout()
    elif active_tab == "shot-analysis-tab":
        return shot_analysis.layout()
    elif active_tab == "xg-difference-tab":
        return xg_difference.layout()
    elif active_tab == "goalkeeping-performance-tab":
        return goalkeeping_performance.layout()  # Render the new layout

# Register callbacks for each module
top_scorers.register_callbacks(app)
player_radar_charts.register_callbacks(app)
transfers_analysis.register_callbacks(app)
club_transfer_details.register_callbacks(app)
home_away_performance.register_callbacks(app)
cl_results.register_callbacks(app)
top_6_race.register_callbacks(app)
shot_analysis.register_callbacks(app)
xg_difference.register_callbacks(app)
goalkeeping_performance.register_callbacks(app)  # Register callbacks for the new module

# Add custom CSS to adjust the font size of the tabs
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .custom-tabs .nav-link {
                font-size: 10.4px;  /* Adjust the font size as needed */
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
