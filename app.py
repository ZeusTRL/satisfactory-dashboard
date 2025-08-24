import dash
from dash import html, dcc, Input, Output
import dash_table
import pandas as pd
import json
from factory_calculator import resolve_inputs

# === Load recipes and prepare dropdown ===
with open("dev_dump.json") as f:
    RAW_RECIPES = json.load(f)

# === Build item name lookup ===
ITEM_NAME_LOOKUP = {}
for recipe in RAW_RECIPES:
    for product in recipe.get("Products", []):
        ITEM_NAME_LOOKUP[product["ItemClass"]] = recipe.get("DisplayName", product["ItemClass"])

# === Build machine name lookup ===
MACHINE_NAME_LOOKUP = {
    "Build_ConstructorMk1_C": "Constructor",
    "Build_AssemblerMk1_C": "Assembler",
    "Build_ManufacturerMk1_C": "Manufacturer",
    "Build_Refinery_C": "Refinery",
    "Build_Packager_C": "Packager",
    "Build_Blender_C": "Blender",
    "Build_SmelterMk1_C": "Smelter",
    "Build_FoundryMk1_C": "Foundry",
    # Add more as needed
}

# === Build product dropdown options from dev_dump.json ===
product_options = []
seen = set()
for recipe in RAW_RECIPES:
    if recipe.get("DisplayName") and recipe.get("Products"):
        for product in recipe["Products"]:
            product_class = product["ItemClass"]
            if product_class not in seen:
                product_options.append({
                    "label": recipe["DisplayName"],
                    "value": product_class
                })
                seen.add(product_class)

# === Dash App Setup ===
app = dash.Dash(__name__)
app.title = "Satisfactory Factory Planner"

app.layout = html.Div([
    html.H1("Satisfactory Factory Dashboard"),

    html.Div([
        html.Label("Include Alternate Recipes?"),
        dcc.Checklist(
            id="alt-recipe-toggle",
            options=[{"label": "Yes", "value": "include"}],
            value=[],
            inline=True,
            style={"marginBottom": "10px"}
        )
    ]),

    html.Div([
        html.Label("Select Product:"),
        dcc.Dropdown(
            id="product-select",
            options=product_options,
            value=product_options[0]["value"] if product_options else None
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

# === Callback Wiring ===
@app.callback(
    Output("machine-summary", "children"),
    Output("input-table", "children"),
    Input("product-select", "value"),
    Input("production-rate", "value"),
    Input("alt-recipe-toggle", "value")
)
def update_dashboard(product_class, rate, alt_toggle):
    use_alternates = "include" in alt_toggle
    print(f"[DEBUG] Selected: {product_class} | Rate: {rate} | Alternates: {use_alternates}")

    chains = resolve_inputs(product_class, rate, use_alternates=use_alternates)

    if not chains:
        return html.Div("⚠️ No valid production chain found."), html.Div()

    machine_blocks = []
    input_blocks = []

    for chain in chains:
        machine_blocks.append(html.Div([
            html.H3(ITEM_NAME_LOOKUP.get(chain['name'], chain['name'])),
            html.Ul([
                html.Li(f"Machine: {MACHINE_NAME_LOOKUP.get(chain['machine'], chain['machine'])}"),
                html.Li(f"Machines Required: {chain['machines']}")
            ])
        ]))

        if chain["inputs"]:
            input_df = pd.DataFrame({
                "Input Resource": [
                    ITEM_NAME_LOOKUP.get(item, item) for item in chain["inputs"].keys()
                ],
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
