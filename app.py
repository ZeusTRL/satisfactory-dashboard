import json
import ast
import dash
from dash import html, dcc, Input, Output, callback
import dash_table

# Load the JSON
with open("dev_dump.json") as f:
    dev_data = json.load(f)

# Separate NativeClasses
item_descriptors = []
recipes_raw = []
machines_raw = []

for entry in dev_data:
    native_class = entry.get("NativeClass", "")
    data = entry.get("Classes", [])

    if native_class == "/Script/CoreUObject.Class'/Script/FactoryGame.FGItemDescriptor'":
        item_descriptors.extend(data)
    elif native_class == "/Script/CoreUObject.Class'/Script/FactoryGame.FGRecipe'":
        recipes_raw.extend(data)
    elif native_class == "/Script/CoreUObject.Class'/Script/FactoryGame.FGBuildableManufacturer'":
        machines_raw.extend(data)

# Index items and machines by ClassName
ITEM_INDEX = {item["ClassName"]: item["mDisplayName"] for item in item_descriptors}
MACHINE_INDEX = {m["ClassName"]: m.get("mDisplayName", m["ClassName"]) for m in machines_raw}

# Build reverse index from product ClassName to recipe object
PRODUCT_TO_RECIPE = {}
for recipe in recipes_raw:
    product_str = recipe.get("mProduct", "")
    try:
        parsed = ast.literal_eval(product_str)
        for product in parsed:
            class_path = product["ItemClass"]
            class_name = class_path.split(".")[-1].replace("'", "")
            if "Alternate" not in recipe["ClassName"]:
                PRODUCT_TO_RECIPE[class_name] = recipe
    except Exception as e:
        print(f"❌ Failed to parse mProduct: {product_str} | Error: {e}")

print(f"🔍 Valid PRODUCT_TO_RECIPE entries: {len(PRODUCT_TO_RECIPE)}")
for k in list(PRODUCT_TO_RECIPE.keys())[:10]:
    print(f"🔸 {k}")

# Construct dropdown options only for valid items
dropdown_options = [
    {'label': ITEM_INDEX.get(prod, prod), 'value': prod}
    for prod in PRODUCT_TO_RECIPE.keys()
    if prod in ITEM_INDEX
]

print(f"🧾 Dropdown will include {len(dropdown_options)} items")

# Dash setup
app = dash.Dash(__name__)
app.title = "Satisfactory Factory Planner"

app.layout = html.Div([
    html.H1("Satisfactory Recipe Dashboard"),
    dcc.Dropdown(id="product-dropdown", options=dropdown_options, placeholder="Select an item"),
    html.Div(id="recipe-output")
])

@callback(
    Output('recipe-output', 'children'),
    [Input('product-dropdown', 'value')]
)
def update_output(product_classname):
    if not product_classname:
        return html.Div()

    recipe = PRODUCT_TO_RECIPE.get(product_classname)
    if not recipe:
        return html.Div(f"No recipe found for {product_classname}")

    def parse_io(raw_str):
        entries = []
        try:
            parsed = ast.literal_eval(raw_str)
            for entry in parsed:
                class_path = entry["ItemClass"]
                class_name = class_path.split(".")[-1].replace("'", "")
                display_name = ITEM_INDEX.get(class_name, class_name)
                entries.append({
                    "Item": display_name,
                    "Amount": entry["Amount"]
                })
        except Exception as e:
            print(f"❌ Error parsing IO: {raw_str} | {e}")
        return entries

    ingredients = parse_io(recipe.get("mIngredients", ""))
    outputs = parse_io(recipe.get("mProduct", ""))
    duration = recipe.get("mManufactoringDuration", "N/A")

    # Extract machine ClassNames
    produced_in_raw = recipe.get("mProducedIn", "")
    try:
        produced_in_list = ast.literal_eval(produced_in_raw)
        machines = []
        for entry in produced_in_list:
            machine_class = entry.split(".")[-1].replace('"', '')
            if machine_class.startswith("Build_"):
                machines.append(MACHINE_INDEX.get(machine_class, machine_class))
    except Exception as e:
        print(f"❌ Error parsing mProducedIn: {produced_in_raw} | {e}")
        machines = [produced_in_raw]  # fallback

    return html.Div([
        html.H2(f"Recipe: {ITEM_INDEX.get(product_classname, product_classname)}"),
        html.P(f"Duration: {duration} seconds"),
        html.P(f"Produced In: {', '.join(machines)}"),

        html.H3("Ingredients"),
        dash_table.DataTable(
            columns=[{"name": k, "id": k} for k in ["Item", "Amount"]],
            data=ingredients,
            style_table={"marginBottom": "20px"}
        ),

        html.H3("Outputs"),
        dash_table.DataTable(
            columns=[{"name": k, "id": k} for k in ["Item", "Amount"]],
            data=outputs,
            style_table={"marginBottom": "40px"}
        )
    ])

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8050)
