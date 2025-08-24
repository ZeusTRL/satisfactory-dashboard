import dash
from dash import dcc, html, Input, Output
import json

# Load the dev_dump.json data
with open("dev_dump.json", "r") as f:
    data = json.load(f)

# Extract dropdown options from FGItemDescriptor entries
product_options = []

for item in data:
    if item.get("NativeClass") == "/Script/CoreUObject.Class'/Script/FactoryGame.FGItemDescriptor'":
        for entry in item.get("Classes", []):
            display_name = entry.get("mDisplayName", "")
            if display_name:  # avoid empty names
                product_options.append(display_name)

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Satisfactory Factory Planner"

# Layout
app.layout = html.Div([
    html.H1("Satisfactory Factory Planner"),
    html.Label("Select a product:"),
    dcc.Dropdown(
        id="product-dropdown",
        options=[{"label": name, "value": name} for name in sorted(product_options)],
        placeholder="Choose an item..."
    ),
    html.Br(),
    html.Div(id="recipe-output")
])

# Callback for recipe output
@app.callback(
    Output("recipe-output", "children"),
    [Input("product-dropdown", "value")]
)
def display_recipe(selected_display_name):
    if not selected_display_name:
        return "Please select an item to view its recipe."

    print(f"🔽 Dropdown selection: {selected_display_name}")

    for item in data:
        if item.get("NativeClass") == "/Script/CoreUObject.Class'/Script/FactoryGame.FGRecipe'":
            for recipe in item.get("Classes", []):
                recipe_display_name = recipe.get("mDisplayName", "")
                recipe_class_name = recipe.get("ClassName", "")

                print(f"🔍 Checking recipe: {recipe_class_name} with display name: {recipe_display_name}")

                if recipe_display_name == selected_display_name and "Alternate" not in recipe_class_name:
                    print(f"✅ Match found for recipe: {recipe_class_name}")

                    ingredients = recipe.get("mIngredients", "[]")
                    products = recipe.get("mProduct", "[]")
                    duration = recipe.get("mManufactoringDuration", "Unknown")

                    return html.Div([
                        html.H4(f"Recipe: {recipe_display_name}"),
                        html.P(f"Duration: {duration} seconds"),
                        html.P(f"Ingredients: {ingredients}"),
                        html.P(f"Products: {products}"),
                    ])

    print("❌ No matching recipe found.")
    return "No recipe found for the selected item."

# Run the server
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
