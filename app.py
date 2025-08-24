import json
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Load dev_dump.json
with open("dev_dump.json", "r") as f:
    data = json.load(f)

# Extract item descriptors and recipe data
item_descriptors = []
recipes = []

for entry in data:
    native_class = entry.get("NativeClass", "")
    classes = entry.get("Classes", [])

    if native_class == "/Script/CoreUObject.Class'/Script/FactoryGame.FGItemDescriptor'":
        item_descriptors.extend(classes)

    elif native_class == "/Script/CoreUObject.Class'/Script/FactoryGame.FGRecipe'":
        recipes.extend(classes)

# Build dropdown options
dropdown_options = [
    {"label": item.get("mDisplayName", item.get("ClassName", "")), "value": item.get("ClassName")}
    for item in item_descriptors
]

# Map ClassName to full descriptor for easy lookup
descriptor_lookup = {item["ClassName"]: item for item in item_descriptors}

# Find a matching recipe using partial ClassName match
def find_recipe_for_product_item(item_classname):
    partial_match = "_" + item_classname.split("_", 1)[-1]
    for recipe in recipes:
        if partial_match in recipe.get("ClassName", "") and item_classname in recipe.get("mProduct", ""):
            return recipe
    return None

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Satisfactory Crafting Dashboard"

app.layout = html.Div([
    html.H1("Satisfactory Crafting Dashboard"),
    dcc.Dropdown(
        id="item-dropdown",
        options=dropdown_options,
        placeholder="Select an item..."
    ),
    html.Div(id="output-container", style={"whiteSpace": "pre-wrap", "marginTop": "20px"})
])

@app.callback(
    Output("output-container", "children"),
    Input("item-dropdown", "value")
)
def update_output(selected_classname):
    if not selected_classname:
        return "Select an item to view its data."

    descriptor = descriptor_lookup.get(selected_classname)
    if not descriptor:
        return f"No data found for {selected_classname}."

    # Try to find a matching recipe
    recipe = find_recipe_for_product_item(selected_classname)

    display_name = descriptor.get("mDisplayName", selected_classname)
    output = f"### {display_name}\n\n"
    output += f"**Descriptor:**\n```json\n{json.dumps(descriptor, indent=4)}\n```"

    if recipe:
        output += f"\n\n**Recipe:**\n```json\n{json.dumps(recipe, indent=4)}\n```"
    else:
        output += "\n\n**No matching recipe found.**"

    return output

if __name__ == "__main__":
    print(f"📦 Total entries in dev_dump.json: {len(data)}")
    print(f"🔧 Valid crafting recipes found: {len(recipes)}")
    print(f"🧪 First few dropdown keys: {[item.get('mDisplayName') for item in item_descriptors[:5]]}")
    app.run_server(debug=True)
