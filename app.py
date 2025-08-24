import json
import dash
from dash import html, dcc, Input, Output
import dash_table

# Load and parse JSON data
with open('dev_dump.json') as f:
    data = json.load(f)

# Build index of item descriptors
ITEM_INDEX = {}
RECIPE_DATA = []

for entry in data:
    native_class = entry.get("NativeClass", "")
    
    if native_class == "/Script/CoreUObject.Class'/Script/FactoryGame.FGItemDescriptor'":
        class_name = entry.get("ClassName", "")
        display_name = entry.get("mDisplayName", "")
        ITEM_INDEX[class_name] = display_name
    
    elif native_class == "/Script/CoreUObject.Class'/Script/FactoryGame.FGRecipe'":
        if "Alternate" not in entry.get("ClassName", ""):
            RECIPE_DATA.append(entry)

# Create dropdown options
dropdown_options = [
    {"label": name, "value": name}
    for name in sorted(set(entry["mDisplayName"] for entry in data
                           if entry.get("NativeClass") == "/Script/CoreUObject.Class'/Script/FactoryGame.FGItemDescriptor'"))
]

# Helper to parse item strings like: (ItemClass="...",Amount=X)
def parse_item_string(raw_string):
    entries = []
    if not raw_string:
        return entries

    parts = raw_string.strip("()").split("),(")
    for part in parts:
        item_class = ""
        amount = 0
        if "ItemClass=" in part and "Amount=" in part:
            try:
                item_class = part.split("ItemClass=")[1].split(",")[0].strip('"').split("/")[-1]
                amount = int(part.split("Amount=")[1].replace(")", ""))
                display_name = ITEM_INDEX.get(item_class, item_class)
                entries.append((display_name, amount))
            except Exception as e:
                print(f"Error parsing part: {part} -> {e}")
    return entries

# Start Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Satisfactory Factory Planner"),
    html.Label("Select a product:"),
    dcc.Dropdown(id='item-dropdown', options=dropdown_options),
    html.Div(id='recipe-output')
])

@app.callback(
    Output('recipe-output', 'children'),
    Input('item-dropdown', 'value')
)
def display_recipe(item_name):
    if not item_name:
        return ""

    output = []

    for recipe in RECIPE_DATA:
        if recipe.get("mDisplayName") != item_name:
            continue
        
        duration = recipe.get("mManufactoringDuration", "?")
        ingredients_raw = recipe.get("mIngredients", "")
        products_raw = recipe.get("mProduct", "")
        produced_in_raw = recipe.get("mProducedIn", "")

        # Parse human-readable format
        ingredients = parse_item_string(ingredients_raw)
        products = parse_item_string(products_raw)
        produced_in = produced_in_raw.replace('"', '').replace("(", "").replace(")", "").split(",")

        recipe_section = [
            html.H3(f"Recipe: {item_name}"),
            html.P(f"Duration: {duration} seconds"),
            html.P(f"Produced In: {', '.join(produced_in)}"),
            html.Strong("Ingredients:"),
            dash_table.DataTable(
                columns=[{"name": "Item", "id": "item"}, {"name": "Amount", "id": "amount"}],
                data=[{"item": item, "amount": amount} for item, amount in ingredients],
                style_table={'width': '60%'}
            ),
            html.Strong("Outputs:"),
            dash_table.DataTable(
                columns=[{"name": "Item", "id": "item"}, {"name": "Amount", "id": "amount"}],
                data=[{"item": item, "amount": amount} for item, amount in products],
                style_table={'width': '60%'}
            ),
            html.Hr()
        ]

        output.extend(recipe_section)

    if not output:
        return html.P("No recipe found for this item.")
    return output

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)
