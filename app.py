import dash
from dash import html, dcc, Input, Output
import dash_table
import plotly.express as px
import pandas as pd
from factory_calculator import calculate_factory

app = dash.Dash(__name__)

# === Layout ===
app.layout = html.Div([
html.Div([
    html.Label("Uranium Reactors:"),
    dcc.Input(id='input-uranium', type='number', min=0, step=1, value=25),

    html.Label("Plutonium Reactors:", style={'marginLeft': '30px'}),
    dcc.Input(id='input-plutonium', type='number', min=0, step=1, value=20),

    html.Label("Ficsonium Reactors:", style={'marginLeft': '30px'}),
    dcc.Input(id='input-ficsonium', type='number', min=0, step=1, value=100),
], style={'marginBottom': '20px'}),

    dcc.Graph(id='production-graph'),

    html.Div(id='totals-summary'),
    html.Div(id='machine-summary'),

    html.H2("Input Resource Breakdown"),

    html.Div(id='uranium-table'),
    html.Div(id='plutonium-table'),
    html.Div(id='ficsonium-table'),

    html.P("Dashboard running inside Docker on LXC container!")
])

# === Callback ===
@app.callback(
    Output('production-graph', 'figure'),
    Output('totals-summary', 'children'),
    Output('machine-summary', 'children'),
    Output('uranium-table', 'children'),
    Output('plutonium-table', 'children'),
    Output('ficsonium-table', 'children'),
    Input('input-uranium', 'value'),
    Input('input-plutonium', 'value'),
    Input('input-ficsonium', 'value')
)
def update_dashboard(uranium_reactors, plutonium_reactors, ficsonium_reactors):
    data = calculate_factory(
    uranium_reactors=uranium_reactors,
    plutonium_reactors=plutonium_reactors,
    ficsonium_reactors=ficsonium_reactors
    )

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

    # === Reactor Totals Summary ===
    reactors = data["Reactors"]
    totals_summary = html.Div([
        html.H2("Reactor Summary"),
        html.Ul([
            html.Li(f"Uranium Reactors: {reactors['Uranium Reactors']}"),
            html.Li(f"Plutonium Reactors: {reactors['Plutonium Reactors']}"),
            html.Li(f"Ficsonium Reactors: {reactors['Ficsonium Reactors']}"),
            html.Li(f"Total Reactors: {reactors['Total']}")
        ])
    ])

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

    # === Helper to convert machine counts to Dash table ===
    def build_machine_summary(name, data_dict):
        machine_data = {k: v for k, v in data_dict.items() if k != "Inputs"}
        table_df = pd.DataFrame({
            "Machine Type": list(machine_data.keys()),
            "Count": list(machine_data.values())
        })
        return html.Div([
            html.H3(f"{name} Machine Summary"),
            dash_table.DataTable(
                columns=[{"name": col, "id": col} for col in table_df.columns],
                data=table_df.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'},
                style_header={'fontWeight': 'bold'}
            )
        ])

    # === Build tables ===
    uranium_table = build_table("Uranium", data["Uranium Fuel Rod Chain"]["Inputs"])
    plutonium_table = build_table("Plutonium", data["Plutonium Fuel Rod Chain"]["Inputs"])
    ficsonium_table = build_table("Ficsonium", data["Ficsonium Fuel Rod Chain"]["Inputs"])

    uranium_machines = build_machine_summary("Uranium", data["Uranium Fuel Rod Chain"])
    plutonium_machines = build_machine_summary("Plutonium", data["Plutonium Fuel Rod Chain"])
    ficsonium_machines = build_machine_summary("Ficsonium", data["Ficsonium Fuel Rod Chain"])

    machine_summary = html.Div([
        html.H2("Machine Count Summary"),
        uranium_machines,
        plutonium_machines,
        ficsonium_machines
    ])

    return fig, totals_summary, machine_summary, uranium_table, plutonium_table, ficsonium_table

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)
