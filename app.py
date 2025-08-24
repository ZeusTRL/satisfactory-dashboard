import json
import dash
from dash import dcc, html, Input, Output
import os

# Load dev_dump.json
with open("dev_dump.json", "r") as f:
    data = json.load(f)

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

# Dash App Setup
app = dash.Dash(__name__)
app.title = "Satisfactory Factory Planner"

app.layout = html.Div([
    html.H1("Satisfactory Factory Planner"),
    html.Label("Select a product:"),
    dcc.Dropdown(
        id='product-dropdown',
        options=dropdown_options,
        placeholder="Select an item"
    ),
    html.Div(id='recipe-output')
])

@app.callback(
    Output('recipe-output', 'children'),
    Input('product-dropdown', 'value')
)
def display_recipe(selected_display_name):
    if not selected_display_name:
        return "Please select an item."

    print(f"[DEBUG] Selected item: {selected_display_name}")

    # Try to find matching recipe by mDisplayName
    matching_recipes = []
    for entry in data:
        if entry.get("NativeClass") == "/Script/CoreUObject.Class'/Script/FactoryGame.FGRecipe'":
            for recipe in entry.get("Classes", []):
                recipe_display_name = recipe.get("mDisplayName", "")
                recipe_class_name = recipe.get("ClassName", "")

                if recipe_display_name == selected_display_name and "Alternate" not in recipe_class_name:
                    print(f"[MATCH] Found matching recipe: {recipe_class_name}")
                    matching_recipes.append(recipe)

    if not matching_recipes:
        print("[INFO] No matching recipe found.")
        return f"No non-alternate recipe found for: {selected_display_name}"

    # Use the first match
    recipe = matching_recipes[0]

    # Parse ingredients
    ingredients_raw = recipe.get("mIngredients", "")
    products_raw = recipe.get("mProduct", "")
    duration = recipe.get("mManufactoringDuration", "Unknown")

    return html.Div([
        html.H3(f"Recipe: {selected_display_name}"),
        html.P(f"Duration: {duration} seconds"),
        html.P(f"Ingredients Raw: {ingredients_raw}"),
        html.P(f"Products Raw: {products_raw}"),
        html.P("You can now parse these fields into a more readable structure.")
    ])

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
