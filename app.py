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

for entry in RAW_RECIPES:
    if not isinstance(entry, dict):
        continue

    # Check if this entry contains a product
    product_name = entry.get("ClassName")
    display_name = entry.get("mDisplayName", product_name)

    if product_name and display_name:
        # Populate lookup
        ITEM_NAME_LOOKUP[product_name] = display_name

        # Simulate a single "recipe" using only this item as a product
        RECIPE_INDEX.setdefault(product_name, []).append({
            "Product": [{"ItemClass": product_name, "Amount": 1}],
            "Ingredients": [],  # you can update this later if needed
            "Machine": "Manual Entry",
            "Time": 1.0
        })



# === Print debug info ===
print(f"📦 Total recipes loaded from dev_dump.json: {len(RAW_RECIPES)}")
print(f"✅ Valid crafting recipes found: {len(RECIPE_INDEX)}")
print(f"🔍 First few RECIPE_INDEX keys: {list(RECIPE_INDEX.keys())[:5]}")

# === Setup Dash app ===
app = dash.Dash(__name__)
app.title = "Satisfactory Factory Dashboard"

product_options = [
    {"label": ITEM_NAME_LOOKUP.get(item_class, item_class), "value": item_class}
    for item_class in RECIPE_INDEX
]

app.layout = html.Div([
    html.H1("Satisfactory Factory Dashboard"),

    dcc.Checklist(
        options=[{"label": "Include Alternate Recipes?", "value": "alt"}],
        value=[],
        id="alt-recipe-toggle"
    ),

    html.Label("Select Product:"),
    dcc.Dropdown(
        id="product-dropdown",
        options=product_options,
        placeholder="Select...",
        style={"width": "50%"}
    ),

    html.Div(id="output-warning", style={"color": "orange", "fontWeight": "bold"}),

    html.H2("Input Resource Breakdown"),
    html.Div(id="input-breakdown"),

    html.P("Dashboard running inside Docker on LXC container.")
])

@app.callback(
    Output("input-breakdown", "children"),
    Output("output-warning", "children"),
    Input("product-dropdown", "value"),
    Input("alt-recipe-toggle", "value")
)
def update_output(product_class, alt_toggle):
    if not product_class:
        return "", ""

    use_alt = "alt" in alt_toggle
    try:
        breakdown = resolve_inputs(product_class, use_alternate=use_alt)
    except Exception as e:
        return "", f"⚠️ Error: {str(e)}"

    if not breakdown:
        return "", "⚠️ No valid production chain found."

    df = pd.DataFrame(breakdown).T.reset_index()
    df.columns = ["Resource", "Rate (per min)"]

    return dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"name": i, "id": i} for i in df.columns],
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "padding": "5px"},
        style_header={"fontWeight": "bold"}
    ), ""

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)
