# import dash
# from dash import html, dcc, Input, Output
# import dash_table
import pandas as pd
import json
from factory_calculator import resolve_inputs

# === Load recipes from dev_dump.json ===
with open("dev_dump.json") as f:
    RAW_RECIPES = json.load(f)

print("Total recipes loaded:", len(RAW_RECIPES))

valid_recipes = 0
for recipe in RAW_RECIPES:
    if "Product" in recipe and isinstance(recipe["Product"], list) and recipe["Product"]:
        valid_recipes += 1

print("Recipes with valid 'Product' lists:", valid_recipes)

# === Build RECIPE_INDEX and ITEM_NAME_LOOKUP locally ===
RECIPE_INDEX = {}
ITEM_NAME_LOOKUP = {}

for recipe in RAW_RECIPES:
    if "Ingredients" not in recipe or "Product" not in recipe:
        continue

    products = recipe["Product"]
    if not isinstance(products, list) or not products:
        continue

    for product in products:
        item_class = product.get("ItemClass")
        if item_class:
            print(f"Found product: {product.get('ItemClass')} - {product.get('DisplayName')}")
            RECIPE_INDEX.setdefault(item_class, []).append(recipe)
            display_name = product.get("DisplayName") or recipe.get("mDisplayName", item_class)
            ITEM_NAME_LOOKUP[item_class] = display_name

# === Build dropdown options ===
product_options = [
    {"label": ITEM_NAME_LOOKUP.get(item_class, item_class), "value": item_class}
    for item_class in RECIPE_INDEX
]

# === Initialize Dash app ===
app = dash.Dash(__name__)
app.title = "Satisfactory Factory Planner"

app.layout = html.Div([
    html.H1("Satisfactory Factory Dashboard"),

    html.Div([
        dcc.Checklist(
            id="alternate-toggle",
            options=[{"label": "Include Alternate Recipes?", "value": "yes"}],
            value=[]
        )
    ], style={"marginBottom": "10px"}),

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

@app.callback(
    Output("machine-summary", "children"),
    Output("input-table", "children"),
    Input("product-select", "value"),
    Input("production-rate", "value"),
    Input("alternate-toggle", "value")
)
def update_dashboard(product_class, rate, toggle_value):
    use_alternates = "yes" in toggle_value
    chains = resolve_inputs(product_class, rate, use_alternates=use_alternates)

    if not chains:
        return html.Div("⚠️ No valid production chain found."), html.Div()

    machine_blocks = []
    input_blocks = []

    for chain in chains:
        machine_blocks.append(html.Div([
            html.H3(ITEM_NAME_LOOKUP.get(chain['name'], chain['name'])),
            html.Ul([
                html.Li(f"Machine: {chain['machine']}"),
                html.Li(f"Machines Required: {chain['machines']}")
            ])
        ]))

        if chain["inputs"]:
            input_df = pd.DataFrame({
                "Input Resource": [ITEM_NAME_LOOKUP.get(item, item) for item in chain["inputs"].keys()],
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
