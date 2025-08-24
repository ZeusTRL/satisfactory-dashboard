import json
import dash
from dash import html, dcc, Input, Output
import dash_table
import re

# Load dev_dump.json
with open('dev_dump.json') as f:
    raw_data = json.load(f)

# Separate item and recipe entries by NativeClass
item_classes = []
recipe_classes = []

for entry in raw_data:
    native_class = entry.get("NativeClass")
    if native_class == "/Script/CoreUObject.Class'/Script/FactoryGame.FGItemDescriptor'":
        item_classes.extend(entry.get("Classes", []))
    elif native_class == "/Script/CoreUObject.Class'/Script/FactoryGame.FGRecipe'":
        recipe_classes.extend(entry.get("Classes", []))

# Build a lookup table for item ClassName -> DisplayName
item_lookup = {item["ClassName"]: item.get("mDisplayName", item["ClassName"]) for item in item_classes}

# Build dropdown options
dropdown_options = [
    {"label": item.get("mDisplayName", item["ClassName"]), "value": item["ClassName"]}
    for item in item_classes
]

# App layout
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Satisfactory Recipe Dashboard"),
    dcc.Dropdown(
        id="item-dropdown",
        options=dropdown_options,
        placeholder="Select an item"
    ),
    html.Div(id="recipe-output")
])

# Parse ingredient string like:
# "((ItemClass=\"...Desc_AluminumScrap_C'\",Amount=6),(ItemClass=\"...Desc_Silica_C'\",Amount=5))"
def parse_item_amount_string(data_str):
    pattern = r"ItemClass=.*?/([^/]+_C)'.*?Amount=(\d+)"
    matches = re.findall(pattern, data_str)
    return [(item_lookup.get(classname, classname), int(amount)) for classname, amount in matches]

@app.callback(
    Output("recipe-output", "children"),
    Input("item-dropdown", "value")
)
def display_recipe(item_classname):
    if not item_classname:
        return ""

    matched_recipes = []
    for recipe in recipe_classes:
        if item_classname in recipe.get("mProduct", ""):
            matched_recipes.append(recipe)

    if not matched_recipes:
        return html.Div("No recipe found for this item.")

    outputs = []
    for recipe in matched_recipes:
        ingredients = parse_item_amount_string(recipe.get("mIngredients", ""))
        products = parse_item_amount_string(recipe.get("mProduct", ""))
        duration = float(recipe.get("mManufactoringDuration", "0"))
        producers = re.findall(r'Build_(\w+)', recipe.get("mProducedIn", ""))

        output = html.Div([
            html.H3("Recipe: " + recipe.get("mDisplayName", "Unknown")),
            html.P(f"Duration: {duration} seconds"),
            html.P(f"Produced In: {', '.join(producers) if producers else 'N/A'}"),

            html.H4("Ingredients:"),
            dash_table.DataTable(
                columns=[{"name": "Item", "id": "item"}, {"name": "Amount", "id": "amount"}],
                data=[{"item": item, "amount": amt} for item, amt in ingredients],
                style_table={'width': '50%'}
            ),

            html.H4("Outputs:"),
            dash_table.DataTable(
                columns=[{"name": "Item", "id": "item"}, {"name": "Amount", "id": "amount"}],
                data=[{"item": item, "amount": amt} for item, amt in products],
                style_table={'width': '50%'}
            ),
            html.Hr()
        ])
        outputs.append(output)

    return outputs

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
