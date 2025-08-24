import json
from math import ceil
from collections import defaultdict

# === Load raw recipe dump ===
with open("dev_dump.json") as f:
    RAW_DUMP = json.load(f)

# === Helper function to filter valid production recipes ===
def extract_valid_recipes(dump_data):
    valid_recipes = []
    for recipe in dump_data:
        # Filter only recipes with products, ingredients, and a machine
        if (
            recipe.get("Products") and recipe.get("Ingredients")
            and recipe.get("ProducedIn") and recipe.get("Duration")
        ):
            # Some ProducedIn fields are lists, some are strings
            if isinstance(recipe["ProducedIn"], list):
                machine = recipe["ProducedIn"][0] if recipe["ProducedIn"] else None
            else:
                machine = recipe["ProducedIn"]
            if machine:
                recipe["__CleanMachine"] = machine.split("/")[-1]
                valid_recipes.append(recipe)
    return valid_recipes

# === Build RECIPE_INDEX from cleaned dump ===
VALID_RECIPES = extract_valid_recipes(RAW_DUMP)

RECIPE_INDEX = {}
for recipe in VALID_RECIPES:
    for product in recipe.get("Products", []):
        product_class = product["ItemClass"]
        RECIPE_INDEX.setdefault(product_class, []).append(recipe)

# === Sort by preferring non-alternates (vanilla) first ===
for product_class in RECIPE_INDEX:
    RECIPE_INDEX[product_class] = sorted(
        RECIPE_INDEX[product_class],
        key=lambda r: ("Alternate" in r["ClassName"], len(r.get("Ingredients", [])))
    )

# === Factory calculation logic ===
def calculate_factory(product_class: str, target_rate: float, use_alternates=False):
    if product_class not in RECIPE_INDEX:
        raise ValueError(f"No recipe found for product '{product_class}'")

    recipe_list = RECIPE_INDEX[product_class]

    # Filter based on toggle
    if not use_alternates:
        recipe_list = [r for r in recipe_list if "Alternate" not in r["ClassName"]]

    if not recipe_list:
        raise ValueError(f"No valid recipe for product '{product_class}' with current toggle")

    # Use top-ranked recipe (first in sorted list)
    recipe = recipe_list[0]

    product_info = next((p for p in recipe["Products"] if p["ItemClass"] == product_class), None)
    if not product_info:
        raise ValueError(f"Product class '{product_class}' not found in recipe products")

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
    summary[chain_name]["Machine Type"] = recipe["__CleanMachine"]
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
