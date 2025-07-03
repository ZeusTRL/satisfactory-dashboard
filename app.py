import dash
from dash import html, dcc, Input, Output
import dash_table
import plotly.express as px
import pandas as pd
from factory_calculator import calculate_factory

app = dash.Dash(__name__)

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

    html.H2("Input Resource Breakdown"),

    html.Div(id='uranium-table'),
    html.Div(id='plutonium-table'),
    html.Div(id='ficsonium-table'),

    html.P("Dashboard running inside Docker on LXC container!")
])

@app.callback(
    Output('production-graph', 'figure'),
    Output('uranium-table', 'children'),
    Output('plutonium-table', 'children'),
    Output('ficsonium-table', 'children'),
    Input('ficsonium-slider', 'value')
)
def update_dashboard(ficsonium_reactors):
    data = calculate_factory(ficsonium_reactors)

    uranium_rate = data["Uranium Fuel Rod Chain"]["Manufacturers"] * 0.4
    plutonium_rate = data["Plutonium Fuel Rod Chain"]["Manufacturers"] * 0.25
    ficsonium_rate = ficsonium_reactors

    # === Bar chart ===
    df = pd.DataFrame({
        "Factory Section": ["Uranium", "Plutonium", "Ficsonium"],
        "Production Rate": [uranium_rate, plutonium_rate, ficsonium_rate]
    })

    fig = px.bar(df, x="Factory Section", y="Production Rate",
                 title=f"Production Rates for {ficsonium_reactors} Ficsonium Reactors")

    # === Helper to convert input dict to Dash table ===
    def build_table(name, input_dict):
        table_df = pd.DataFrame({
            "Input Resource": list(input_dict.keys()),
            "Amount per Minute": list(input_dict.values())
        })
        return html.Div([
            html.H3(f"{name} Inputs"),
            dash_table.DataTable(
                columns=[{"name": col, "id": col} for col in table_df.columns],
                data=table_df.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'},
                style_header={'fontWeight': 'bold'}
            )
        ])

    # === Extract and convert inputs ===
    uranium_table = build_table("Uranium", data["Uranium Fuel Rod Chain"]["Inputs"])
    plutonium_table = build_table("Plutonium", data["Plutonium Fuel Rod Chain"]["Inputs"])
    ficsonium_table = build_table("Ficsonium", data["Ficsonium Fuel Rod Chain"]["Inputs"])

    return fig, uranium_table, plutonium_table, ficsonium_table

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)
