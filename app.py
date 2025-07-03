import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from factory_calculator import calculate_factory

app = dash.Dash(__name__)

# Initial layout
app.layout = html.Div([
    html.H1("Satisfactory Factory Dashboard"),
    
    html.Label("Number of Ficsonium Reactors:"),
    dcc.Slider(
        id='ficsonium-slider',
        min=25,
        max=200,
        step=5,
        value=100,
        marks={i: str(i) for i in range(25, 201, 25)}
    ),

    dcc.Graph(id='production-graph'),

    html.P("Dashboard running inside Docker on LXC container!")
])

# Callback to update graph based on slider input
@app.callback(
    Output('production-graph', 'figure'),
    Input('ficsonium-slider', 'value')
)
def update_graph(ficsonium_reactors):
    data = calculate_factory(ficsonium_reactors)

    uranium_rate = data["Uranium Fuel Rod Chain"]["Manufacturers"] * 0.4
    plutonium_rate = data["Plutonium Fuel Rod Chain"]["Manufacturers"] * 0.25
    ficsonium_rate = ficsonium_reactors  # 1 per reactor

    df = pd.DataFrame({
        "Factory Section": ["Uranium", "Plutonium", "Ficsonium"],
        "Production Rate": [uranium_rate, plutonium_rate, ficsonium_rate]
    })

    fig = px.bar(df, x="Factory Section", y="Production Rate",
                 title=f"Production Rates for {ficsonium_reactors} Ficsonium Reactors")
    return fig

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)
