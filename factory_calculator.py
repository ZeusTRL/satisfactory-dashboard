### === factory_calculator.py ===

import json
from math import ceil
from collections import defaultdict

# === Load recipes from JSON ===
with open("satisfactory_recipes.json") as f:
    raw_recipes = json.load(f)

# === Index recipes by product name ===
RECIPE_INDEX = {}
for entry in raw_recipes:
    name = entry.get("NAME")
    if name:
        RECIPE_INDEX[name] = entry

def calculate_factory(product: str, target_rate: float):
    if product not in RECIPE_INDEX:
        raise ValueError(f"Product '{product}' not found in recipe index.")

    recipe = RECIPE_INDEX[product]
    machine = recipe.get("MACHINE", "Unknown")
    per_min = float(recipe.get("PER-MIN", 0))
    if per_min == 0:
        raise ValueError(f"Invalid rate per minute for {product}")

    multiplier = target_rate / per_min
    machine_count = ceil(multiplier)

    inputs = {}
    for i in range(1, 5):
        name_key = f"IN{i}-NAME"
        qty_key = f"IN{i}-QTY"
        name = recipe.get(name_key)
        qty = recipe.get(qty_key)
        if name and qty:
            cycle_time = float(recipe.get("CYCLE", 60))
            inputs[name] = float(qty) * multiplier * (60 / cycle_time)

    chain_name = f"{product} Production Chain"
    summary = defaultdict(dict)
    summary[chain_name]["Machine Type"] = machine
    summary[chain_name]["Machines Required"] = machine_count
    summary[chain_name]["Inputs"] = inputs

    return summary

def resolve_inputs(product: str, rate: float, visited=None):
    if visited is None:
        visited = set()

    if product in visited:
        return []
    visited.add(product)

    try:
        summary = calculate_factory(product, rate)
    except ValueError:
        return []

    chain_key = list(summary.keys())[0]
    chain_data = summary[chain_key]

    chains = [{
        "name": product,
        "machine": chain_data["Machine Type"],
        "machines": chain_data["Machines Required"],
        "inputs": chain_data["Inputs"]
    }]

    for input_item, input_rate in chain_data["Inputs"].items():
        subchains = resolve_inputs(input_item, input_rate, visited)
        chains.extend(subchains)

    return chains