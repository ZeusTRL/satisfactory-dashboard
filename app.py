import dash
from dash import html, dcc, Input, Output
import dash_table
import plotly.express as px
import pandas as pd
import json
from factory_calculator import calculate_factory

# === Load available product names from recipe file ===
with open("satisfactory_recipes.json") as f:
    raw_recipes = json.load(f)

PRODUCT_OPTIONS = [
    {"label": entry["NAME"], "value": entry["NAME"]}
    for entry in raw_recipes if "NAME" in entry
]

# === Initialize Dash app ===
app = dash.Dash(__name__)
app.title = "Satisfactory Factory Planner"

# === Layout ===
app.layout = html.Div([
    html.H1("Satisfactory Factory Dashboard"),

    html.Div([
        html.Label("Select Product:"),
        dcc.Dropdown(
            id="product-select",
            options=PRODUCT_OPTIONS,
            value="Ficsonium Fuel Rod"
        ),
    ], style={"marginBottom": "15px"}),

    html.Div([
        html.Label("Target Production Rate (per minute):"),
        dcc.Input(id="production-rate", type="number", min=1, step=1, value=100),
    ], style={"marginBottom": "25px"}),

    dcc.Graph(id="production-graph"),

    html.Div(id="machine-summary", style={"marginTop": "25px"}),

    html.H2("Input Resource Breakdown"),
    html.Div(id="input-table"),

    html.P("Dashboard running inside Docker on LXC container.")
])

# === Callback ===
@app.callback(
    Output("production-graph", "figure"),
    Output("machine-summary", "children"),
    Output("input-table", "children"),
    Input("product-select", "value"),
    Input("production-rate", "value")
)
def update_dashboard(product, rate):
    data = calculate_factory(product, rate)

    chain_key = list(data.keys())[0]
    chain_data = data[chain_key]

    machine_type = chain_data.get("Machine Type", "Unknown")
    machine_count = chain_data.get("Machines Required", 0)
    inputs = chain_data.get("Inputs", {})

    # === Bar chart of total production rate ===
    df_chart = pd.DataFrame({
        "Product": [product],
        "Production Rate": [rate]
    })
    fig = px.bar(df_chart, x="Product", y="Production Rate",
                 title=f"Production Rate for {product} ({rate}/min)")

    # === Machine Summary Table ===
    machine_summary = html.Div([
        html.H2("Machine Summary"),
        html.Ul([
            html.Li(f"Machine Type: {machine_type}"),
            html.Li(f"Machines Required: {machine_count}")
        ])
    ])

    # === Input Resource Table ===
    input_df = pd.DataFrame({
        "Input Resource": list(inputs.keys()),
        "Amount per Minute": list(inputs.values())
    })

    input_table = dash_table.DataTable(
        columns=[{"name": col, "id": col} for col in input_df.columns],
        data=input_df.to_dict("records"),
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left"},
        style_header={"fontWeight": "bold"}
    )

    return fig, machine_summary, input_table


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050)
