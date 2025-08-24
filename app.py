import dash
from dash import html, dcc, Input, Output, dash_table
# import dash_table
import pandas as pd
import json
from factory_calculator import resolve_inputs

# === Load recipes from dev_dump.json ===
with open("dev_dump.json") as f:
    RAW_RECIPES = json.load(f)

print(f"📦 Total recipes loaded from dev_dump.json: {len(RAW_RECIPES)}")

# === DEBUG: Inspect structure of first few recipes ===
print("\n📦 Sample dev_dump.json entry (pretty):")
print(json.dumps(RAW_RECIPES[0], indent=2))

for i, recipe in enumerate(RAW_RECIPES[:5]):
    print(f"\n🔹 Entry {i} keys:")
    for k in recipe.keys():
        print(f"  - {k}")

# === Build RECIPE_INDEX and ITEM_NAME_LOOKUP locally ===
RECIPE_INDEX = {}
ITEM_NAME_LOOKUP = {}

valid_count = 0
for recipe in RAW_RECIPES:
    if "Ingredients" not in recipe or "Product" not in recipe:
        continue

    products = recipe["Product"]
    if not isinstance(products, list) or not products:
        continue

    for product in products:
        item_class = product.get("ItemClass")
        if item_class:
            RECIPE_INDEX.setdefault(item_class, []).append(recipe)

            display_name = product.get("DisplayName") or recipe.get("mDisplayName", item_class)
            ITEM_NAME_LOOKUP[item_class] = display_name
            valid_count += 1

print(f"✅ Valid crafting recipes found: {valid_count}")
print(f"📄 First few RECIPE_INDEX keys: {list(RECIPE_INDEX.keys())[:5]}")

# === Build dropdown options ===
product_options = [
    {"label": ITEM_NAME_LOOKUP.get(item_class, item_class), "value": item_class}
    for item_class in RECIPE_INDEX
]

# === Initialize Dash App ===
app = dash.Dash(__name__)
app.title = "Satisfactory Factory Dashboard"

app.layout = html.Div([
    html.H2("Satisfactory Factory Dashboard"),
    dcc.Checklist(
        id="include-alternate",
        options=[{"label": "Include Alternate Recipes?", "value": "yes"}],
        value=[]
    ),
    html.Label("Select Product:"),
    dcc.Dropdown(id="product-dropdown", options=product_options, placeholder="Select..."),
    html.Label("Target Production Rate (per minute):"),
    dcc.Input(id="target-rate", type="number", value=100),
    html.Div(id="production-chain"),
    html.H4("Input Resource Breakdown"),
    html.Div(id="input-breakdown"),
    html.Div("Dashboard running inside Docker on LXC container.", style={"marginTop": "2rem"})
])

@app.callback(
    Output("production-chain", "children"),
    Output("input-breakdown", "children"),
    Input("product-dropdown", "value"),
    Input("target-rate", "value"),
    Input("include-alternate", "value")
)
def update_dashboard(product_class, target_rate, include_alts):
    if not product_class or not target_rate:
        return "⚠️ No valid production chain found.", None

    use_alts = "yes" in include_alts
    try:
        resolved_chain, input_breakdown = resolve_inputs(
            product_class, target_rate, use_alts, RAW_RECIPES
        )
    except Exception as e:
        return f"❌ Error: {e}", None

    production_elements = []
    for item in resolved_chain:
        name = ITEM_NAME_LOOKUP.get(item["Item"], item["Item"])
        production_elements.append(html.H5(f"{name}"))
        production_elements.append(html.Ul([
            html.Li(f"Machine: {item['Machine']}"),
            html.Li(f"Machines Required: {item['MachineCount']}")
        ]))

    breakdown_tables = []
    for item_name, amount in input_breakdown.items():
        label = ITEM_NAME_LOOKUP.get(item_name, item_name)
        df = pd.DataFrame([{
            "Input Resource": label,
            "Amount per Minute": round(amount, 2)
        }])
        breakdown_tables.append(html.H5(f"{label} Inputs"))
        breakdown_tables.append(dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": i, "id": i} for i in df.columns],
            style_table={"overflowX": "auto"},
        ))

    return production_elements, breakdown_tables

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
