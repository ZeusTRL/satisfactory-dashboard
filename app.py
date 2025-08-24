import json
import dash
from dash import html, dcc, Input, Output, dash_table
import os

# Load data
with open("dev_dump.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract item descriptors and recipes
item_descriptors = []
recipes = []

for entry in data:
    native_class = entry.get("NativeClass", "")
    if native_class == "/Script/CoreUObject.Class'/Script/FactoryGame.FGItemDescriptor'":
        item_descriptors.extend(entry.get("Classes", []))
    elif native_class == "/Script/CoreUObject.Class'/Script/FactoryGame.FGRecipe'":
        recipes.extend(entry.get("Classes", []))

print(f"🧾 Total entries in dev_dump.json: {len(data)}")
print(f"🛠️  Valid crafting recipes found: {len(recipes)}")

# Build index: {DisplayName: ClassData}
RECIPE_INDEX = {}
for item in item_descriptors:
    display_name = item.get("mDisplayName")
    if display_name:
        RECIPE_INDEX[display_name] = item

print(f"🔑 First few RECIPE_INDEX keys: {list(RECIPE_INDEX.keys())[:5]}")

# Build dropdown options
dropdown_options = [{"label": name, "value": name} for name in RECIPE_INDEX.keys()]

# Setup Dash app
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

@app.callback(
    Output("recipe-output", "children"),
    Input("item-dropdown", "value")
)
def display_recipe(selected_item_name):
    if not selected_item_name:
        return ""

    item_data = RECIPE_INDEX.get(selected_item_name)
    if not item_data:
        return html.Div("Item data not found.")

    item_class = item_data.get("ClassName", "")
    item_base = item_class.replace("Desc_", "").replace("_C", "")
    expected_recipe_class = f"Recipe_{item_base}_C"

    matched_recipes = []
    for recipe in recipes:
        recipe_class = recipe.get("ClassName", "")
        if recipe_class == expected_recipe_class:
            matched_recipes.append(recipe)

    if not matched_recipes:
        return html.Div("No matching recipe found for this item.")

    output = []

    for recipe in matched_recipes:
        output.append(html.H3(f"Recipe: {recipe.get('mDisplayName', 'Unknown')}"))
        output.append(html.P(f"Duration: {recipe.get('mManufactoringDuration', 'N/A')} seconds"))

        produced_in = recipe.get("mProducedIn", "")
        output.append(html.P(f"Produced In: {produced_in}"))

        def parse_ingredients(key):
            raw = recipe.get(key, "")
            items = []
            if raw.startswith("((") and raw.endswith("))"):
                raw = raw[1:-1]  # strip first and last ()
            for part in raw.split("),("):
                try:
                    class_part = part.split("ItemClass=")[1].split(",")[0]
                    amount_part = part.split("Amount=")[1].split(")")[0]
                    items.append({"Item": class_part.split("/")[-1].replace("'", ""), "Amount": int(amount_part)})
                except (IndexError, ValueError):
                    continue
            return items

        ingredients = parse_ingredients("mIngredients")
        outputs = parse_ingredients("mProduct")

        output.append(html.H4("Ingredients:"))
        output.append(dash_table.DataTable(
            columns=[{"name": "Item", "id": "Item"}, {"name": "Amount", "id": "Amount"}],
            data=ingredients,
            style_table={'width': '50%'}
        ))

        output.append(html.H4("Outputs:"))
        output.append(dash_table.DataTable(
            columns=[{"name": "Item", "id": "Item"}, {"name": "Amount", "id": "Amount"}],
            data=outputs,
            style_table={'width': '50%'}
        ))

        output.append(html.Hr())

    return output

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
