import dash
from dash import html, dcc, Input, Output
import json
import ast
import re

# Load your JSON data
with open("dev_dump.json") as f:
    dev_data = json.load(f)

# Extract recipes, items, and machines from the correct NativeClass
recipes, items, machines = [], [], []

for entry in dev_data:
    native_class = entry.get("NativeClass", "")
    data = entry.get("Classes", [])

    if native_class == "/Script/CoreUObject.Class'/Script/FactoryGame.FGItemDescriptor'":
        items.extend(data)
    elif native_class == "/Script/CoreUObject.Class'/Script/FactoryGame.FGRecipe'":
        recipes.extend(data)
    elif native_class == "/Script/CoreUObject.Class'/Script/FactoryGame.FGBuildableManufacturer'":
        machines.extend(data)

# Build item lookup for ClassName -> DisplayName
ITEM_INDEX = {
    item.get("ClassName", ""): item.get("mDisplayName", "Unknown Item")
    for item in items
}

# Build machine lookup for Build_ClassName -> DisplayName
MACHINE_INDEX = {
    m.get("ClassName", ""): m.get("mDisplayName", "Unknown Machine")
    for m in machines
    if m.get("ClassName", "").startswith("Build_")
}

# Build product-to-recipe index
PRODUCT_TO_RECIPE = {}

for recipe in recipes:
    product_str = recipe.get("mProduct", "")
    try:
        product_list = ast.literal_eval(product_str)
        for product in product_list:
            class_path = product["ItemClass"]
            class_name = class_path.split(".")[-1].replace('"', "")
            PRODUCT_TO_RECIPE[class_name] = recipe
    except Exception:
        pass

# Setup Dash app
app = dash.Dash(__name__)
app.title = "Satisfactory Factory Planner"

app.layout = html.Div([
    html.H1("Satisfactory Recipe Dashboard"),
    dcc.Dropdown(
        id='product-dropdown',
        options=[{'label': ITEM_INDEX.get(prod, prod), 'value': prod} for prod in PRODUCT_TO_RECIPE],
        placeholder="Select a product",
        style={'width': '100%'}
    ),
    html.Div(id='recipe-output')
])


def parse_item_string(raw_string):
    """Extracts [(ClassName, Amount)] from raw mIngredients/mProduct string."""
    parsed_items = []
    try:
        item_data = ast.literal_eval(raw_string)
        for entry in item_data:
            class_path = entry["ItemClass"]
            amount = entry["Amount"]
            class_name = class_path.split(".")[-1].replace('"', '')
            parsed_items.append((class_name, amount))
    except Exception:
        pass
    return parsed_items


def get_display_name(class_name):
    return ITEM_INDEX.get(class_name, class_name)


@app.callback(
    Output('recipe-output', 'children'),
    [Input('product-dropdown', 'value')]
)
def update_output(product_classname):
    if not product_classname:
        return ""

    recipe = PRODUCT_TO_RECIPE.get(product_classname)
    if not recipe:
        return html.P("No recipe found.")

    ingredients = parse_item_string(recipe.get("mIngredients", ""))
    products = parse_item_string(recipe.get("mProduct", ""))
    duration = float(recipe.get("mManufactoringDuration", "0"))
    produced_in_raw = recipe.get("mProducedIn", "")

    # Parse only Build_ class names and lookup
    machine_classnames = re.findall(r'Build_[^".]+_C', produced_in_raw)
    machine_display_names = [MACHINE_INDEX.get(m, m) for m in machine_classnames]

    return html.Div([
        html.H3(f"Recipe: {recipe.get('mDisplayName', 'Unknown')}"),
        html.P(f"Duration: {duration:.6f} seconds"),
        html.P(f"Produced In: {', '.join(machine_display_names)}"),
        html.H4("Ingredients:"),
        html.Table([
            html.Thead(html.Tr([html.Th("Item"), html.Th("Amount")])),
            html.Tbody([
                html.Tr([html.Td(get_display_name(i)), html.Td(str(a))])
                for i, a in ingredients
            ])
        ]),
        html.H4("Outputs:"),
        html.Table([
            html.Thead(html.Tr([html.Th("Item"), html.Th("Amount")])),
            html.Tbody([
                html.Tr([html.Td(get_display_name(p)), html.Td(str(a))])
                for p, a in products
            ])
        ])
    ])


if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0")
