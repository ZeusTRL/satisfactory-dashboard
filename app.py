import json
import dash
import dash_table
from dash import dcc, html, Input, Output

# Load the JSON data
with open("dev_dump.json", "r") as f:
    dev_data = json.load(f)

# Separate the entries by NativeClass
items = []
recipes = []

for entry in dev_data:
    native_class = entry.get("NativeClass", "")
    data = entry.get("Classes", [])

    if native_class == "/Script/CoreUObject.Class'/Script/FactoryGame.FGItemDescriptor'":
        items.extend(data)
    elif native_class == "/Script/CoreUObject.Class'/Script/FactoryGame.FGRecipe'":
        recipes.extend(data)

# Build lookup dictionaries

ITEM_DISPLAY_LOOKUP = {
    item.get("ClassName", ""): item.get("mDisplayName", "") for item in items
}

def parse_entries(raw_str):
    entries = []
    if not raw_str:
        return entries
    parts = raw_str.strip("()").split("),(")
    for part in parts:
        if not part:
            continue
        item_class_path = part.split("ItemClass=")[-1].split(",")[0].strip('"')
        amount_part = part.split("Amount=")[-1].replace(")", "")
        raw_class_name = item_class_path.split("/")[-1]
        clean_class_name = raw_class_name.split(".")[-1]

        display_name = ITEM_DISPLAY_LOOKUP.get(clean_class_name, clean_class_name)
        entries.append({
            "Item": f"{display_name} ({clean_class_name})",
            "Amount": int(amount_part) if amount_part.isdigit() else amount_part
        })
    return entries

RECIPE_INDEX = {item.get("mDisplayName", "Unknown"): item for item in items}
CLASSNAME_TO_DISPLAYNAME = {item.get("ClassName", ""): item.get("mDisplayName", "") for item in items}

dropdown_options = [{"label": name, "value": name} for name in RECIPE_INDEX]

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Satisfactory Recipe Dashboard"

app.layout = html.Div([
    html.H1("Satisfactory Factory Planner"),
    dcc.Dropdown(
        id="item-dropdown",
        options=dropdown_options,
        placeholder="Select a product:"
    ),
    html.Div(id="recipe-output")
])

@app.callback(
    Output("recipe-output", "children"),
    [Input("item-dropdown", "value")]
)
def update_output(selected_name):
    if not selected_name:
        return html.Div()

    selected_item = RECIPE_INDEX.get(selected_name, {})
    item_display = selected_item.get("mDisplayName", "")
    matched_recipes = []

    for recipe in recipes:
        recipe_name = recipe.get("mDisplayName", "")
        recipe_class = recipe.get("ClassName", "")
        ingredients_raw = recipe.get("mIngredients", "")
        products_raw = recipe.get("mProduct", "")
        print(f"🧪 Raw Ingredients String: {ingredients_raw}")
        print(f"🧪 Raw Products String: {products_raw}")
        if recipe_name == item_display and "Alternate" not in recipe_class:
            matched_recipes.append(recipe)

    if not matched_recipes:
        return html.Div(f"No standard recipe found for {selected_name}")
    
    print(f"✅ Found {len(matched_recipes)} recipe(s) for '{selected_name}'")
    for r in matched_recipes:
        print(f"➡️ Recipe ClassName: {r.get('ClassName')}, DisplayName: {r.get('mDisplayName')}")


    def parse_entries(raw_str):
        entries = []
        if not raw_str:
            return entries
        parts = raw_str.strip("()").split("),(")
        for part in parts:
            try:
                item_str = part.split("ItemClass=")[-1].split(",")[0]
                item_class = item_str.split("/")[-1].replace('"', '').replace("'", "")
                amount = part.split("Amount=")[-1].replace(")", "")
                display_name = CLASSNAME_TO_DISPLAYNAME.get(item_class, item_class)
                entries.append({
                    "Item": display_name,
                    "Amount": int(amount) if amount.isdigit() else amount
                })
            except Exception as e:
                print(f"⚠️ Failed to parse part: {part} — {e}")
        return entries

    recipe_components = []
    for recipe in matched_recipes:
        duration = recipe.get("mManufactoringDuration", "N/A")
        produced_in_raw = recipe.get("mProducedIn", "")
        produced_in = [x.split(".")[-1].replace('"', '').replace(")", '') for x in produced_in_raw.split(",")]

        ingredients = parse_entries(recipe.get("mIngredients", ""))
        outputs = parse_entries(recipe.get("mProduct", ""))

        recipe_components.append(html.Div([
            html.H3(f"Recipe: {recipe.get('mDisplayName', 'Unnamed')}"),
            html.P(f"Duration: {duration} seconds"),
            html.P(f"Produced In: {', '.join(produced_in)}"),
            html.Strong("Ingredients:"),
            dash_table.DataTable(
                columns=[{"name": k, "id": k} for k in ["Item", "Amount"]],
                data=ingredients,
                style_table={"marginBottom": "20px"},
                style_cell={'textAlign': 'left', 'padding': '5px'},
                style_header={'fontWeight': 'bold'}
            ),
            html.Strong("Outputs:"),
            dash_table.DataTable(
                columns=[{"name": k, "id": k} for k in ["Item", "Amount"]],
                data=outputs,
                style_table={"marginBottom": "40px"},
                style_cell={'textAlign': 'left', 'padding': '5px'},
                style_header={'fontWeight': 'bold'}
            )
        ]))

    return html.Div(recipe_components)

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
