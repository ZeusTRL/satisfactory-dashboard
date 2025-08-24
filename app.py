import dash
from dash import html, dcc, Input, Output
import dash_table
import pandas as pd
import json
import pprint
from factory_calculator import resolve_inputs

# === Load recipes from dev_dump.json ===
with open("dev_dump.json") as f:
    RAW_RECIPES = json.load(f)

# === Build RECIPE_INDEX and ITEM_NAME_LOOKUP locally ===
RECIPE_INDEX = {}
ITEM_NAME_LOOKUP = {}

for recipe in RAW_RECIPES:
    if "mIngredients" not in recipe or "mProduct" not in recipe:
        continue

    products = recipe["mProduct"]
    if not isinstance(products, list) or not products:
        continue

    for product in products:
        item_class = product.get("ItemClass")
        if item_class:
            RECIPE_INDEX.setdefault(item_class, []).append(recipe)

            display_name = product.get("DisplayName") or recipe.get("mDisplayName") or item_class
            ITEM_NAME_LOOKUP[item_class] = display_name


# === Debugging: Print counts and a few entries ===
# print("🔍 Sample raw recipe:")
# pprint.pprint(RAW_RECIPES[0])
print("🔍 Total recipes loaded from dev_dump.json:", len(RAW_RECIPES))
print("🔍 Total items with valid recipes:", len(RECIPE_INDEX))
print("🔍 First few RECIPE_INDEX keys:")
for k in list(RECIPE_INDEX.keys())[:5]:
    print(f"  - {k}: {ITEM_NAME_LOOKUP.get(k, k)}")

# === Build dropdown options ===
product_options = [
    {"label": ITEM_NAME_LOOKUP.get(item_class, item_class), "value": item_class}
    for item_class in RECIPE_INDEX
]

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

@app.callback(
    Output("machine-summary", "children"),
    Output("input-table", "children"),
    Input("product-select", "value"),
    Input("production-rate", "value"),
    Input("alt-recipe-toggle", "value")
)
def update_dashboard(product_class, rate, alt_toggle):
    use_alternates = "include" in alt_toggle
    print(f"📦 Selected: {product_class} | Rate: {rate} | Use Alternates: {use_alternates}")

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
