import json
import re
import dash
from dash import dcc, html, Input, Output

# Load the data
with open('dev_dump.json', 'r') as f:
    data = json.load(f)

# Filter items and recipes by NativeClass
items = []
recipes = []

for entry in data:
    native_class = entry.get("NativeClass", "")
    if native_class == "/Script/CoreUObject.Class'/Script/FactoryGame.FGItemDescriptor'":
        items.append(entry)
    elif native_class == "/Script/CoreUObject.Class'/Script/FactoryGame.FGRecipe'":
        recipes.append(entry)

# Build lookup dicts
ITEM_INDEX = {item["ClassName"]: item.get("mDisplayName", item["ClassName"]) for item in items}
RECIPE_INDEX = {recipe["mDisplayName"]: recipe for recipe in recipes}

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Satisfactory Factory Planner"

app.layout = html.Div([
    html.H1("Satisfactory Factory Planner"),
    html.Label("Select a product:"),
    dcc.Dropdown(
        id='item-dropdown',
        options=[{'label': item['mDisplayName'], 'value': item['mDisplayName']} for item in items],
        placeholder="Select an item"
    ),
    html.Div(id='recipe-output')
])

# Updated parse function using regex
def parse_item_string(raw_string):
    entries = []
    if not raw_string:
        return entries

    pattern = r'ItemClass="[^"]*Desc_([A-Za-z0-9_]+_C)".*?Amount=(\d+)'
    matches = re.findall(pattern, raw_string)

    for class_suffix, amount in matches:
        full_class_name = f"Desc_{class_suffix}"
        display_name = ITEM_INDEX.get(full_class_name, full_class_name)
        entries.append((display_name, int(amount)))

    return entries

# Format ingredient/product entries into Dash table
def make_table(title, entries):
    return html.Div([
        html.H5(title),
        html.Table([
            html.Tr([html.Th("Item"), html.Th("Amount")])] +
            [html.Tr([html.Td(name), html.Td(amount)]) for name, amount in entries]
        )
    ])

@app.callback(
    Output('recipe-output', 'children'),
    [Input('item-dropdown', 'value')]
)
def display_recipe(selected_name):
    if not selected_name:
        return ""

    matched_recipes = [
        recipe for recipe in recipes
        if recipe.get("mDisplayName") == selected_name and "Alternate" not in recipe.get("ClassName", "")
    ]

    if not matched_recipes:
        return html.Div("No recipe found for this item.")

    output = []

    for recipe in matched_recipes:
        ingredients = parse_item_string(recipe.get("mIngredients", ""))
        products = parse_item_string(recipe.get("mProduct", ""))
        duration = recipe.get("mManufactoringDuration", "Unknown")
        produced_in = recipe.get("mProducedIn", "")

        output.append(html.Div([
            html.H4(f"Recipe: {recipe.get('mDisplayName')}"),
            html.P(f"Duration: {duration} seconds"),
            html.P(f"Produced In: {produced_in}"),
            make_table("Ingredients", ingredients),
            make_table("Products", products),
            html.Hr()
        ]))

    return output

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
