import dash
from dash import html, dcc, Input, Output
import dash_table
import pandas as pd
import json
from factory_calculator import resolve_inputs

# === Load raw dev_dump.json ===
with open("dev_dump.json") as f:
    RAW_RECIPES = json.load(f)

# === Filter valid recipes ===
RECIPES = [entry['Classes'] for entry in RAW_RECIPES if entry.get('NativeClass') == '/Script/FactoryGame.FGRecipe']

print(f"📦 Total recipes loaded from dev_dump.json: {len(RAW_RECIPES)}")
print(f"✅ Valid crafting recipes found: {len(RECIPES)}")

# === Build RECIPE_INDEX and ITEM_NAME_LOOKUP ===
RECIPE_INDEX = {}
ITEM_NAME_LOOKUP = {}

for recipe in RECIPES:
    if "mIngredients" not in recipe or "mProduct" not in recipe:
        continue

    products = recipe["mProduct"]
    if not isinstance(products, list) or not products:
        continue

    for product in products:
        item_class = product.get("ItemClass")
        if item_class:
            RECIPE_INDEX.setdefault(item_class, []).append(recipe)

            display_name = product.get("DisplayName") or recipe.get("mDisplayName", item_class)
            ITEM_NAME_LOOKUP[item_class] = display_name

print(f"🧪 First few RECIPE_INDEX keys: {list(RECIPE_INDEX.keys())[:5]}")

# === Build dropdown options ===
product_options = [
    {"label": ITEM_NAME_LOOKUP.get(item_class, item_class), "value": item_class}
    for item_class in RECIPE_INDEX
]

# === Dash App Setup ===
app = dash.Dash(__name__)
app.title = "Satisfactory Factory Dashboard"

app.layout = html.Div([
    html.H2("Satisfactory Factory Dashboard"),
    dcc.Checklist(
        id="alternate-toggle",
        options=[{"label": "Yes", "value": "include"}],
        value=[],
        labelStyle={"display": "inline-block", "margin-right": "10px"},
    ),
    html.Label("Include Alternate Recipes?"),
    html.Br(),
    html.Label("Select Product:"),
    dcc.Dropdown(id="product-dropdown", options=product_options),
    html.Br(),
    html.Label("Target Production Rate (per minute):"),
    dcc.Input(id="target-rate", type="number", value=100),
    html.Br(), html.Br(),
    html.Div(id="output-recipes"),
    html.H3("Input Resource Breakdown"),
    html.Div(id="input-breakdown"),
    html.Br(),
    html.Div("Dashboard running inside Docker on LXC container.", style={"fontSize": 12, "color": "gray"}),
])

@app.callback(
    [Output("output-recipes", "children"),
     Output("input-breakdown", "children")],
    [Input("product-dropdown", "value"),
     Input("target-rate", "value"),
     Input("alternate-toggle", "value")]
)
def update_dashboard(selected_product, target_rate, alt_toggle):
    if not selected_product or target_rate is None:
        return "⚠️ No valid production chain found.", ""

    include_alternates = "include" in alt_toggle
    resolved_chain = resolve_inputs(selected_product, target_rate, RECIPE_INDEX, include_alternates)

    if not resolved_chain:
        return "⚠️ No valid production chain found.", ""

    output_sections = []
    input_sections = []

    for recipe_data in resolved_chain:
        name = recipe_data["recipe_name"]
        machine = recipe_data["machine"]
        count = recipe_data["machine_count"]
        inputs = recipe_data["inputs"]

        output_sections.append(html.Div([
            html.H4(name),
            html.Ul([
                html.Li(f"Machine: {machine}"),
                html.Li(f"Machines Required: {count}")
            ])
        ]))

        input_rows = [
            html.Tr([html.Td(input["item"]), html.Td(input["amount"])])
            for input in inputs
        ]

        input_sections.append(html.Div([
            html.H5(f"{name} Inputs"),
            dash_table.DataTable(
                columns=[{"name": "Input Resource", "id": "item"},
                         {"name": "Amount per Minute", "id": "amount"}],
                data=[{"item": input["item"], "amount": input["amount"]} for input in inputs],
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "left", "padding": "5px"},
            )
        ]))

    return output_sections, input_sections

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
