import json
from math import ceil
from collections import defaultdict

# === Load recipes from the new clean JSON file ===
with open("clean_recipes.json") as f:
    RAW_RECIPES = json.load(f)

# === Build recipe index with preferred sorting ===
RECIPE_INDEX = {}

for recipe in RAW_RECIPES:
    if len(recipe.get("Ingredients", [])) == 0 or len(recipe.get("Products", [])) == 0:
        continue
    for product in recipe.get("Products", []):
        RECIPE_INDEX.setdefault(product["ItemClass"], []).append(recipe)

# Sort each recipe list to prefer vanilla first (non-alternate)
for k in RECIPE_INDEX:
    RECIPE_INDEX[k] = sorted(
        RECIPE_INDEX[k], key=lambda r: ("Alternate" in r["ClassName"], len(r.get("Ingredients", [])))
    )

def is_alternate_recipe(r):
    return "Alternate" in r["ClassName"] or r["ClassName"].lower().startswith("recipe_alt")

def calculate_factory(product_class: str, target_rate: float, use_alternates=False):
    if product_class not in RECIPE_INDEX:
        raise ValueError(f"No recipe found for product '{product_class}'")

    recipe_list = RECIPE_INDEX[product_class]

    print(f"USE ALTERNATES? {use_alternates}")
    print("Available recipes:")
    for r in recipe_list:
        print(" -", r["ClassName"])

    if not use_alternates:
        filtered = [r for r in recipe_list if not is_alternate_recipe(r)]
        recipe = filtered[0] if filtered else recipe_list[0]
    else:
        recipe = recipe_list[0]

    print("Using recipe:", recipe["ClassName"])

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

def resolve_inputs(product_class: str, rate: float, use_alternates=False, visited=None, depth=0, max_depth=6):
    if visited is None:
        visited = set()

    if product_class in visited or depth > max_depth:
        return []
    visited.add(product_class)

    try:
        summary = calculate_factory(product_class, rate, use_alternates=use_alternates)
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
        subchains = resolve_inputs(input_item, input_rate, use_alternates, visited, depth + 1, max_depth)
        chains.extend(subchains)

    return chains
