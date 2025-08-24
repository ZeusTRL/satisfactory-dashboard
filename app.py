import dash
from dash import html, dcc, Input, Output
import dash_table
import pandas as pd
import json

from factory_calculator import resolve_inputs

# === Load recipes from dev_dump.json ===
with open("dev_dump.json") as f:
    RAW_RECIPES = json.load(f)

# === Build RECIPE_INDEX and ITEM_NAME_LOOKUP ===
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

print(f"✔️ Total recipes loaded from dev_dump.json: {len(RAW_RECIPES)}")
print(f"✔️ Total items with valid recipes: {len(RECIPE_INDEX)}")
print(f"✔️ First few RECIPE_INDEX keys: {list(RECIPE_INDEX.keys())[:5]}")

# === Build dropdown options ===
product_options = [
    {"label": ITEM_NAME_LOOKUP.get(item_class, item_class), "value": item_class}
    for item_class in sorted(RECIPE_INDEX)
]

# === Start Dash app ===
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Satisfactory Factory Dashboard"),

    html.Div([
        dcc.Checklist(
            id='include-alternates',
            options=[{'label': 'Yes', 'value': 'include'}],
            value=[],
            inline=True
        ),
        html.Label("Include Alternate Recipes?"),
    ]),

    html.Div([
        html.Label("Select Product:"),
        dcc.Dropdown(
            id='product-dropdown',
            options=product_options,
            placeholder="Select...",
            searchable=True
        ),
    ]),

    html.Div([
        html.Label("Target Production Rate (per minute):"),
        dcc.Input(id='target-rate', type='number', value=100),
    ]),

    html.Div(id='output-recipes'),
    html.H2("Input Resource Breakdown"),
    html.Div(id='input-table'),
    html.Div("Dashboard running inside Docker on LXC container.")
])

@app.callback(
    Output('output-recipes', 'children'),
    Output('input-table', 'children'),
    Input('product-dropdown', 'value'),
    Input('target-rate', 'value'),
    Input('include-alternates', 'value')
)
def update_dashboard(selected_product, target_rate, alternates):
    if not selected_product or not target_rate:
        return html.Div("⚠️ No valid production chain found."), None

    include_alternates = 'include' in alternates
    resolved_data = resolve_inputs(selected_product, target_rate, RECIPE_INDEX, ITEM_NAME_LOOKUP, include_alternates)

    recipe_outputs = []
    input_breakdown = []

    if resolved_data:
        for item, data in resolved_data['recipes'].items():
            label = ITEM_NAME_LOOKUP.get(item, item)
            recipe_outputs.append(html.H3(f"{label}"))
            recipe_outputs.append(html.Ul([
                html.Li(f"Machine: {data['recipe'].get('mProducedIn', ['N/A'])[0]}"),
                html.Li(f"Machines Required: {data['machines']}")
            ]))

        for item, data in resolved_data['inputs'].items():
            label = ITEM_NAME_LOOKUP.get(item, item)
            df = pd.DataFrame([{"Input Resource": label, "Amount per Minute": data["amount"]}])
            input_breakdown.append(html.H4(f"{label} Inputs"))
            input_breakdown.append(dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{"name": i, "id": i} for i in df.columns],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'},
            ))
    else:
        recipe_outputs.append(html.Div("⚠️ No valid production chain found."))

    return recipe_outputs, input_breakdown

if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8050, debug=False)
