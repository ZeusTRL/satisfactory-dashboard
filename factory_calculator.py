from math import ceil
from collections import defaultdict

def calculate_factory(ficsonium_reactors=100, uranium_reactors=None, plutonium_reactors=None):
    summary = defaultdict(dict)

    # === Reactor Setup ===
    if plutonium_reactors is None:
        plutonium_reactors = ficsonium_reactors // 5
    if uranium_reactors is None:
        uranium_reactors = ficsonium_reactors // 4

    # === Reactor Setup ===
    plutonium_reactors = ficsonium_reactors // 5
    uranium_reactors = ficsonium_reactors // 4

    # === Uranium Chain ===
    uranium_fuel_rod_needed = uranium_reactors * 0.2
    uranium_fuel_rod_manufacturers = ceil(uranium_fuel_rod_needed / 0.4)
    encased_uranium_cell_blenders = ceil((20 * uranium_fuel_rod_manufacturers) / 25)
    uranium_ore_needed = 50 * encased_uranium_cell_blenders
    concrete_for_encased_cells = 15 * encased_uranium_cell_blenders
    sulfuric_acid_for_encased_cells = 40 * encased_uranium_cell_blenders
    sulfuric_acid_returned = 10 * encased_uranium_cell_blenders
    encased_steel_beams_needed = 1.2 * uranium_fuel_rod_manufacturers
    electro_rods_uranium = 2 * uranium_fuel_rod_manufacturers
    electro_rod_assemblers_uranium = ceil(electro_rods_uranium / 4)
    stators_uranium = 6 * electro_rod_assemblers_uranium
    ai_limiters_uranium = 4 * electro_rod_assemblers_uranium

    summary["Uranium Fuel Rod Chain"] = {
        "Manufacturers": uranium_fuel_rod_manufacturers,
        "Blenders": encased_uranium_cell_blenders,
        "Assemblers": electro_rod_assemblers_uranium,
        "Inputs": {
            "Uranium Ore": uranium_ore_needed,
            "Concrete": concrete_for_encased_cells,
            "Sulfuric Acid": sulfuric_acid_for_encased_cells - sulfuric_acid_returned,
            "Encased Steel Beams": encased_steel_beams_needed,
            "Stators": stators_uranium,
            "AI Limiters": ai_limiters_uranium
        }
    }

    # === Plutonium Chain ===
    plutonium_fuel_rod_needed = plutonium_reactors * 0.1
    plutonium_fuel_rod_manufacturers = ceil(plutonium_fuel_rod_needed / 0.25)
    encased_plutonium_cell_assemblers = ceil((7.5 * plutonium_fuel_rod_manufacturers) / 5)
    plutonium_pellets_needed = 10 * encased_plutonium_cell_assemblers
    plutonium_pellet_accelerators = ceil(plutonium_pellets_needed / 30)
    non_fissile_uranium_needed = 100 * plutonium_pellet_accelerators
    uranium_waste_for_pellets = 25 * plutonium_pellet_accelerators
    non_fissile_blenders = ceil(non_fissile_uranium_needed / 50)
    uranium_waste_for_non_fissile = 37.5 * non_fissile_blenders
    silica_needed = 10 * non_fissile_blenders
    nitric_acid_needed = 15 * non_fissile_blenders
    sulfuric_acid_for_plutonium = 15 * non_fissile_blenders
    concrete_for_plutonium_cells = 20 * encased_plutonium_cell_assemblers
    steel_beams_plutonium = 4.5 * plutonium_fuel_rod_manufacturers
    heat_sinks_needed = 2.5 * plutonium_fuel_rod_manufacturers
    electro_rods_plutonium = 1.5 * plutonium_fuel_rod_manufacturers
    electro_rod_assemblers_plutonium = ceil(electro_rods_plutonium / 4)
    stators_plutonium = 6 * electro_rod_assemblers_plutonium
    ai_limiters_plutonium = 4 * electro_rod_assemblers_plutonium

    summary["Plutonium Fuel Rod Chain"] = {
        "Manufacturers": plutonium_fuel_rod_manufacturers,
        "Assemblers": encased_plutonium_cell_assemblers,
        "Accelerators (Pellets)": plutonium_pellet_accelerators,
        "Blenders (Non-Fissile)": non_fissile_blenders,
        "Assemblers (Rods)": electro_rod_assemblers_plutonium,
        "Inputs": {
            "Uranium Waste (Pellet)": uranium_waste_for_pellets,
            "Uranium Waste (Non-Fissile)": uranium_waste_for_non_fissile,
            "Silica": silica_needed,
            "Nitric Acid": nitric_acid_needed,
            "Sulfuric Acid": sulfuric_acid_for_plutonium,
            "Concrete": concrete_for_plutonium_cells,
            "Steel Beams": steel_beams_plutonium,
            "Heat Sinks": heat_sinks_needed,
            "Stators": stators_plutonium,
            "AI Limiters": ai_limiters_plutonium
        }
    }

    # === Ficsonium Chain ===
    ficsonium_fuel_rod_needed = ficsonium_reactors
    ficsonium_encoders = ceil(ficsonium_fuel_rod_needed / 2.5)
    ficsonium_needed = 5 * ficsonium_encoders
    electro_rods_ficsonium = 5 * ficsonium_encoders
    ficsite_trigon_needed = 100 * ficsonium_encoders
    excited_photonic_matter_needed = 50 * ficsonium_encoders
    dark_matter_residue_returned = 50 * ficsonium_encoders
    ficsonium_accelerators = ceil(ficsonium_needed / 10)
    plutonium_waste_for_ficsonium = 10 * ficsonium_accelerators
    singularity_cell_needed = 10 * ficsonium_accelerators
    dark_matter_residue_for_ficsonium = 20 * ficsonium_accelerators
    singularity_manufacturers = ceil(singularity_cell_needed / 10)
    nuclear_pasta_needed = 1 * singularity_manufacturers
    dark_matter_crystal_needed = 20 * singularity_manufacturers
    iron_plates_singularity = 100 * singularity_manufacturers
    concrete_singularity = 200 * singularity_manufacturers
    dark_matter_crystal_accelerators = ceil(dark_matter_crystal_needed / 30)
    diamonds_needed = 30 * dark_matter_crystal_accelerators
    dark_matter_residue_for_crystal = 150 * dark_matter_crystal_accelerators
    nuclear_pasta_accelerators = ceil(nuclear_pasta_needed / 0.5)
    copper_powder_needed = 100 * nuclear_pasta_accelerators
    pressure_cube_needed = 0.5 * nuclear_pasta_accelerators
    ficsite_trigon_constructors = ceil(ficsite_trigon_needed / 30)
    ficsite_ingot_needed = 10 * ficsite_trigon_constructors
    dark_matter_residue_total_needed = (
        dark_matter_residue_for_ficsonium + dark_matter_residue_for_crystal - dark_matter_residue_returned
    )
    dark_matter_converters = ceil(dark_matter_residue_total_needed / 100)
    reanimated_sam_needed = 50 * dark_matter_converters
    electro_rod_assemblers_ficsonium = ceil(electro_rods_ficsonium / 4)
    stators_ficsonium = 6 * electro_rod_assemblers_ficsonium
    ai_limiters_ficsonium = 4 * electro_rod_assemblers_ficsonium

    summary["Ficsonium Fuel Rod Chain"] = {
        "Quantum Encoders": ficsonium_encoders,
        "Accelerators (Ficsonium)": ficsonium_accelerators,
        "Singularity Manufacturers": singularity_manufacturers,
        "Accelerators (Crystals)": dark_matter_crystal_accelerators,
        "Accelerators (Pasta)": nuclear_pasta_accelerators,
        "Constructors (Ficsite Trigon)": ficsite_trigon_constructors,
        "Converters (Dark Matter Residue)": dark_matter_converters,
        "Assemblers (Control Rods)": electro_rod_assemblers_ficsonium,
        "Inputs": {
            "Plutonium Waste": plutonium_waste_for_ficsonium,
            "Singularity Cells": singularity_cell_needed,
            "Dark Matter Residue (Net)": dark_matter_residue_total_needed,
            "Diamonds": diamonds_needed,
            "Copper Powder": copper_powder_needed,
            "Pressure Conversion Cube": pressure_cube_needed,
            "Ficsite Ingots": ficsite_ingot_needed,
            "Excited Photonic Matter": excited_photonic_matter_needed,
            "Iron Plates": iron_plates_singularity,
            "Concrete": concrete_singularity,
            "Reanimated SAM": reanimated_sam_needed,
            "Stators": stators_ficsonium,
            "AI Limiters": ai_limiters_ficsonium
        }
    }

    summary["Reactors"] = {
        "Uranium Reactors": uranium_reactors,
        "Plutonium Reactors": plutonium_reactors,
        "Ficsonium Reactors": ficsonium_reactors,
        "Total": uranium_reactors + plutonium_reactors + ficsonium_reactors
    }

    return summary
