import dash
from dash import html, dcc, Input, Output
import dash_table
import pandas as pd
import json
from factory_calculator import resolve_inputs

# === Load recipes from dev_dump.json ===
with open("dev_dump.json") as f:
    RAW_RECIPES = json.load(f)

print(f"📦 Total recipes loaded from dev_dump.json: {len(RAW_RECIPES)}")

# === Build RECIPE_INDEX and ITEM_NAME_LOOKUP ===
RECIPE_INDEX = {}
ITEM_NAME_LOOKUP = {}

valid_recipe_count = 0

for recipe in RAW_RECIPES:
    # Skip non-crafting recipes
    if not recipe.get("Ingredients") or not recipe.get("Product"):
        continue

    # Extract product info
    products = recipe["Product"]
    if not isinstance(products, list):
        continue

    for product in products:
        item_class = product.get("ItemClass")
        if not item_class:
            continue

        # Save display name
        display_name = product.get("DisplayName") or recipe.get("mDisplayName") or item_class
        ITEM_NAME_LOOKUP[item_class] = display_name

        # Add to recipe index
        RECIPE_INDEX.setdefault(item_class, []).append(recipe)
        valid_recipe_count += 1

print(f"✅ Valid crafting recipes found: {valid_recipe_count}")
print(f"🔁 First few RECIPE_INDEX keys: {list(RECIPE_INDEX.keys())[:5]}")

# === Create dropdown options ===
product_options = [
    {"label": ITEM_NAME_LOOKUP.get(item_class, item_class), "value": item_class}
    for item_class in RECIPE_INDEX
]

# === Dash App Layout ===
app = dash.Dash(__name__)
app.title = "Satisfactory Factory Dashboard"

app.layout = html.Div([
    html.H2("Satisfactory Factory Dashboard"),
    dcc.Checklist(
        id="alternate-toggle",
        options=[{"label": "Yes", "value": "Yes"}],
        value=[],
        labelStyle={'display': 'inline-block'}
    ),
    html.Label("Include Alternate Recipes?"),

    html.Label("Select Product:"),
    dcc.Dropdown(id="product-dropdown", options=product_options),

    html.Label("Target Production Rate (per minute):"),
    dcc.Input(id="rate-input", type="number", value=100),

    html.Div(id="output-recipes"),
    html.H4("Input Resource Breakdown"),
    html.Div(id="output-inputs"),

    html.Div("Dashboard running inside Docker on LXC container.", style={"marginTop": "40px", "fontStyle": "italic"})
])


@app.callback(
    Output("output-recipes", "children"),
    Output("output-inputs", "children"),
    Input("product-dropdown", "value"),
    Input("rate-input", "value"),
    Input("alternate-toggle", "value")
)
def update_output(product_class, target_rate, toggle_value):
    if not product_class or not target_rate:
        return "⚠️ No valid production chain found.", ""

    use_alternates = "Yes" in toggle_value

    breakdown, input_summary = resolve_inputs(
        product_class,
        target_rate,
        use_alternate_recipes=use_alternates,
        RECIPE_INDEX=RECIPE_INDEX,
        ITEM_NAME_LOOKUP=ITEM_NAME_LOOKUP
    )

    recipe_display = []
    for step in breakdown:
        label = ITEM_NAME_LOOKUP.get(step["ItemClass"], step["ItemClass"])
        recipe_display.append(html.H5(label))
        recipe_display.append(html.Ul([
            html.Li(f"Machine: {step['Machine']}"),
            html.Li(f"Machines Required: {step['MachineCount']}")
        ]))

    input_tables = []
    for item_class, amount in input_summary.items():
        label = ITEM_NAME_LOOKUP.get(item_class, item_class)
        df = pd.DataFrame({
            "Input Resource": [label],
            "Amount per Minute": [amount]
        })
        input_tables.append(html.H5(f"{label} Inputs"))
        input_tables.append(dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in df.columns],
            data=df.to_dict("records"),
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'},
        ))

    return recipe_display, input_tables


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)
