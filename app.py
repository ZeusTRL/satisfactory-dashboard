import dash
from dash import html, dcc, Input, Output
import dash_table
import pandas as pd
import json
from factory_calculator import resolve_inputs

# === Load product list ===
with open("satisfactory_recipes.json") as f:
    raw_recipes = json.load(f)

PRODUCT_OPTIONS = [
    {"label": entry["NAME"], "value": entry["NAME"]}
    for entry in raw_recipes if "NAME" in entry
]

app = dash.Dash(__name__)
app.title = "Satisfactory Factory Planner"

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

    html.Div(id="machine-summary", style={"marginTop": "25px"}),

    html.H2("Input Resource Breakdown"),
    html.Div(id="input-table"),

    html.P("Dashboard running inside Docker on LXC container.")
])

@app.callback(
    Output("machine-summary", "children"),
    Output("input-table", "children"),
    Input("product-select", "value"),
    Input("production-rate", "value")
)
def update_dashboard(product, rate):
    chains = resolve_inputs(product, rate)

    machine_blocks = []
    input_blocks = []

    for chain in chains:
        machine_blocks.append(html.Div([
            html.H3(f"{chain['name']}"),
            html.Ul([
                html.Li(f"Machine: {chain['machine']}"),
                html.Li(f"Machines Required: {chain['machines']}")
            ])
        ]))

        if chain["inputs"]:
            input_df = pd.DataFrame({
                "Input Resource": list(chain["inputs"].keys()),
                "Amount per Minute": list(chain["inputs"].values())
            })

            input_blocks.append(html.Div([
                html.H4(f"{chain['name']} Inputs"),
                dash_table.DataTable(
                    columns=[{"name": col, "id": col} for col in input_df.columns],
                    data=input_df.to_dict("records"),
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "left"},
                    style_header={"fontWeight": "bold"}
                )
            ]))

    return html.Div(machine_blocks), html.Div(input_blocks)

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050)
