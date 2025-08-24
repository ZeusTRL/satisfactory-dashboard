import json
import dash
from dash import dcc, html, Input, Output

# Load dev_dump.json
with open("dev_dump.json", "r") as f:
    data = json.load(f)

# Separate items and recipes by NativeClass
items_by_classname = {}
recipes = []

for entry in data:
    native_class = entry.get("NativeClass", "")
    if native_class == "/Script/CoreUObject.Class'/Script/FactoryGame.FGItemDescriptor'":
        for item in entry.get("Classes", []):
            class_name = item.get("ClassName")
            display_name = item.get("mDisplayName")
            if class_name and display_name:
                items_by_classname[class_name] = display_name
    elif native_class == "/Script/CoreUObject.Class'/Script/FactoryGame.FGRecipe'":
        for recipe in entry.get("Classes", []):
            recipes.append(recipe)

# Initialize Dash app
app = dash.Dash(__name__)

# Dropdown options from mDisplayName
dropdown_options = [{"label": name, "value": name} for name in items_by_classname.values()]

app.layout = html.Div([
    html.H1("Satisfactory Factory Planner"),
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
def display_recipe(selected_name):
    if not selected_name:
        return ""

    # Find the ClassName for the selected mDisplayName
    selected_class_name = None
    for class_name, display_name in items_by_classname.items():
        if display_name == selected_name:
            selected_class_name = class_name
            break

    if not selected_class_name:
        return "Item not found."

    # Derive the item base name for matching recipe class
    item_base = selected_class_name.replace("Desc_", "").replace("_C", "")
    print(f"\n🔽 Selected item: {selected_name}")
    print(f"🔍 Looking for recipes ending in: {item_base}_C")

    matching_recipe = None
    for recipe in recipes:
        recipe_class = recipe.get("ClassName", "")
        if recipe_class.endswith(f"{item_base}_C") and "Alternate" not in recipe_class:
            print(f"✅ Matched recipe: {recipe_class}")
            matching_recipe = recipe
            break
        else:
            print(f"⛔ Skipped: {recipe_class}")

    if not matching_recipe:
        return "No matching recipe found."

    # Display recipe details
    output = []
    output.append(html.H3(f"Recipe: {matching_recipe.get('mDisplayName', 'Unknown')}"))

    ingredients_str = matching_recipe.get("mIngredients", "")
    product_str = matching_recipe.get("mProduct", "")
    duration = matching_recipe.get("mManufactoringDuration", "N/A")
    produced_in = matching_recipe.get("mProducedIn", "")

    output.append(html.P(f"Duration: {duration} seconds"))
    output.append(html.P(f"Produced In: {produced_in}"))

    # Parse and display ingredients
    output.append(html.H4("Ingredients:"))
    ingredients_clean = ingredients_str.replace("),(", ")|(").strip("()").split("|")
    for ing in ingredients_clean:
        try:
            item_part, amt_part = ing.split(",Amount=")
            item_name = item_part.split("/")[-1].replace("_C'", "").replace("'", "")
            amount = int(amt_part.strip(")"))
            output.append(html.P(f"{amount} x {item_name}"))
        except Exception as e:
            output.append(html.P(f"Failed to parse ingredient: {ing}"))

    # Parse and display product(s)
    output.append(html.H4("Output:"))
    products_clean = product_str.replace("),(", ")|(").strip("()").split("|")
    for prod in products_clean:
        try:
            item_part, amt_part = prod.split(",Amount=")
            item_name = item_part.split("/")[-1].replace("_C'", "").replace("'", "")
            amount = int(amt_part.strip(")"))
            output.append(html.P(f"{amount} x {item_name}"))
        except Exception as e:
            output.append(html.P(f"Failed to parse product: {prod}"))

    return output

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
