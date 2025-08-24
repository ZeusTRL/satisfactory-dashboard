import json
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output

# Load and parse data
with open("dev_dump.json", "r") as file:
    data = json.load(file)

# ✅ Filter items with the correct NativeClass
valid_classes = []
for entry in data:
    if entry.get("NativeClass") == "/Script/CoreUObject.Class'/Script/FactoryGame.FGItemDescriptor'":
        valid_classes.extend(entry.get("Classes", []))

# ✅ Build recipe index from mDisplayName
RECIPE_INDEX = {
    item.get("mDisplayName"): item
    for item in valid_classes
    if item.get("mDisplayName")
}

# Optional: Debug prints
print(f"✅ Total entries in dev_dump.json: {len(data)}")
print(f"🛠️ Valid crafting recipes found: {len(RECIPE_INDEX)}")
print(f"🔍 First few RECIPE_INDEX keys: {list(RECIPE_INDEX.keys())[:5]}")

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Satisfactory Crafting Dashboard"

# Layout
app.layout = html.Div([
    html.H1("Satisfactory Crafting Dashboard"),
    dcc.Dropdown(
        id='recipe-selector',
        options=[{'label': name, 'value': name} for name in RECIPE_INDEX.keys()],
        placeholder='Select a recipe'
    ),
    html.Div(id='recipe-details')
])

# Callback to show recipe details
@app.callback(
    Output('recipe-details', 'children'),
    Input('recipe-selector', 'value')
)
def display_recipe_details(selected_name):
    if not selected_name:
        return html.P("Please select a recipe.")

    item = RECIPE_INDEX[selected_name]
    # Display all fields for now
    return html.Div([
        html.H2(selected_name),
        html.Pre(json.dumps(item, indent=2))
    ])

# Run app
if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8050, debug=True)
