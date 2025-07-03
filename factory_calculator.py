import json
from math import ceil
from collections import defaultdict

# === Load recipes from the pretty JSON file ===
with open("saitsfactory_recipes.json") as f:
    raw_recipes = json.load(f)

# === Index recipes by product name ===
RECIPE_INDEX = {}
for entry in raw_recipes:
    name = entry.get("NAME")
    if name:
        RECIPE_INDEX[name] = entry

def calculate_factory(product: str, target_rate: float):
    """
    Calculates required machines and input rates to produce the selected product at the target rate per minute.
    """
    if product not in RECIPE_INDEX:
        raise ValueError(f"Product '{product}' not found in recipe index.")

    recipe = RECIPE_INDEX[product]

    # Base recipe info
    machine = recipe.get("MACHINE", "Unknown")
    per_min = float(recipe.get("PER-MIN", 0))
    if per_min == 0:
        raise ValueError(f"Invalid rate per minute for {product}")

    multiplier = target_rate / per_min
    machine_count = ceil(multiplier)

    # Calculate per-minute input rates
    inputs = {}
    for i in range(1, 5):
        name_key = f"IN{i}-NAME"
        qty_key = f"IN{i}-QTY"
        name = recipe.get(name_key)
        qty = recipe.get(qty_key)

        if name and qty:
            cycle_time = float(recipe.get("CYCLE", 60))
            inputs[name] = float(qty) * multiplier * (60 / cycle_time)

    # Return dashboard-compatible summary
    chain_name = f"{product} Production Chain"
    summary = defaultdict(dict)

    summary[chain_name]["Machine Type"] = machine
    summary[chain_name]["Machines Required"] = machine_count
    summary[chain_name]["Inputs"] = inputs

    return summary
