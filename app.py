import json
import dash
import dash_table
from dash import dcc, html, Input, Output

# Load the JSON data
with open("dev_dump.json", "r") as f:
    dev_data = json.load(f)

# Parse all item descriptors (for dropdown)
item_descriptors = {}
for entry in data:
    if entry.get("NativeClass") == "/Script/CoreUObject.Class'/Script/FactoryGame.FGItemDescriptor'":
        for item in entry.get("Classes", []):
            display_name = item.get("mDisplayName")
            if display_name:
                item_descriptors[display_name] = item

# Extract display names for the dropdown
dropdown_options = [{"label": name, "value": name} for name in sorted(item_descriptors.keys())]

print(f"📦 Total entries in dev_dump.json: {len(dev_data)}")
print(f"🛠️ Valid crafting recipes found: {len(recipes)}")

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Satisfactory Recipe Dashboard"

app.layout = html.Div([
    html.H1("Satisfactory Recipe Dashboard"),
    dcc.Dropdown(
        id="item-dropdown",
        options=dropdown_options,
        placeholder="Select an item"
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
    item_classname = selected_item.get("ClassName", "")

    # Convert Desc_IronPlate_C -> IronPlate
    item_base = item_classname.replace("Desc_", "").replace("_C", "")
    expected_recipe_class = f"Recipe_{item_base}_C"

    print(f"\n🔽 Selected item: {selected_name}")
    print(f"🔎 Looking for recipes with ClassName: {expected_recipe_class}")

    matched_recipes = []
    for recipe in recipes:
        recipe_class = recipe.get("ClassName", "")
        display_name = recipe.get("mDisplayName", "N/A")

        if expected_recipe_class == recipe_class and "Alternate" not in recipe_class:
            print(f"✅ MATCH: {recipe_class} | {display_name}")
            matched_recipes.append(recipe)
        else:
            print(f"❌ SKIP: {recipe_class} | {display_name}")

    if not matched_recipes:
        return html.Div(f"No standard recipe found for {selected_name}")

    recipe_components = []
    for recipe in matched_recipes:
        duration = recipe.get("mManufactoringDuration", "N/A")
        produced_in_raw = recipe.get("mProducedIn", "")
        produced_in = [x.split(".")[-1].replace('"', '') for x in produced_in_raw.split(",")]

        ingredients_raw = recipe.get("mIngredients", "")
        products_raw = recipe.get("mProduct", "")

        def parse_entries(raw_str):
            entries = []
            if not raw_str:
                return entries
            parts = raw_str.strip("()").split("),(")
            for part in parts:
                if not part:
                    continue
                item_class_part = part.split("ItemClass=")[-1].split(",")[0].strip('"').split("/")[-1]
                amount_part = part.split("Amount=")[-1].replace(")", "")
                entries.append({
                    "Item": item_class_part,
                    "Amount": int(amount_part) if amount_part.isdigit() else amount_part
                })
            return entries

        ingredients = parse_entries(ingredients_raw)
        outputs = parse_entries(products_raw)

        recipe_components.append(html.Div([
            html.H3(f"Recipe: {recipe.get('mDisplayName', 'Unnamed')}"),
            html.P(f"Duration: {duration} seconds"),
            html.P(f"Produced In: {', '.join(produced_in)}"),
            html.Strong("Ingredients:"),
            dash_table.DataTable(
                columns=[{"name": k, "id": k} for k in ["Item", "Amount"]],
                data=ingredients,
                style_table={"marginBottom": "20px"}
            ),
            html.Strong("Outputs:"),
            dash_table.DataTable(
                columns=[{"name": k, "id": k} for k in ["Item", "Amount"]],
                data=outputs,
                style_table={"marginBottom": "40px"}
            )
        ]))

    return html.Div(recipe_components)

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
