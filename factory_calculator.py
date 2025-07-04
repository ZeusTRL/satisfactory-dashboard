import json
from math import ceil
from collections import defaultdict

# === Load recipes from the new clean JSON file ===
with open("clean_recipes.json") as f:
    RAW_RECIPES = json.load(f)

# === Build recipe index with preferred sorting ===
RECIPE_INDEX = {}

def is_clean_recipe(r):
    return (
        "Alternate" not in r["ClassName"]
        and "Christmas" not in r["ClassName"]
        and len(r.get("Ingredients", [])) > 0
        and len(r.get("Products", [])) > 0
    )

for recipe in RAW_RECIPES:
    if not is_clean_recipe(recipe):
        continue
    for product in recipe.get("Products", []):
        RECIPE_INDEX.setdefault(product["ItemClass"], []).append(recipe)

# Prefer recipes with fewer ingredients (simplest path)
for k in RECIPE_INDEX:
    RECIPE_INDEX[k] = sorted(RECIPE_INDEX[k], key=lambda r: len(r.get("Ingredients", [])))

def calculate_factory(product_class: str, target_rate: float):
    if product_class not in RECIPE_INDEX:
        raise ValueError(f"No recipe found for product '{product_class}'")

    recipe = RECIPE_INDEX[product_class][0]  # Use preferred recipe

    product_info = next((p for p in recipe["Products"] if p["ItemClass"] == product_class), None)
    if not product_info:
        raise ValueError(f"Product class '{product_class}' not found in product list")

    produced_per_cycle = product_info["Amount"]
    cycle_time = float(recipe["Duration"])
    per_minute = (produced_per_cycle / cycle_time) * 60
    multiplier = target_rate / per_minute
    machine_count = ceil(multiplier)

    inputs = {}
    for ing in recipe.get("Ingredients", []):
        ing_rate = (ing["Amount"] / cycle_time) * 60 * multiplier
        inputs[ing["ItemClass"]] = ing_rate

    chain_name = f"{product_class} Production Chain"
    summary = defaultdict(dict)
    summary[chain_name]["Machine Type"] = recipe.get("ProducedIn", ["Unknown"])[0].split("/")[-1]
    summary[chain_name]["Machines Required"] = machine_count
    summary[chain_name]["Inputs"] = inputs

    return summary

def resolve_inputs(product_class: str, rate: float, visited=None, depth=0, max_depth=6):
    if visited is None:
        visited = set()

    if product_class in visited or depth > max_depth:
        return []
    visited.add(product_class)

    try:
        summary = calculate_factory(product_class, rate)
    except ValueError:
        return []

    chain_key = list(summary.keys())[0]
    chain_data = summary[chain_key]

    chains = [{
        "name": product_class,
        "machine": chain_data["Machine Type"],
        "machines": chain_data["Machines Required"],
        "inputs": chain_data["Inputs"]
    }]

    for input_item, input_rate in chain_data["Inputs"].items():
        subchains = resolve_inputs(input_item, input_rate, visited, depth + 1, max_depth)
        chains.extend(subchains)

    return chains
