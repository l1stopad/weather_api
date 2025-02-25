import re
import os
import json
from pathlib import Path



def load_city_mappings(file_path: str = "app/city_mappings/city_mappings.json") -> dict:
    # Resolve absolute path
    full_path = Path(file_path).resolve()
    if not full_path.exists():
        raise ValueError(f"City mappings file {full_path} not found.")
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_regions(file_path: str = "app/regions/regions.json") -> dict:
    # Resolve absolute path
    full_path = Path(file_path).resolve()
    if not full_path.exists():
        raise ValueError(f"Region file {full_path} not found.")
    with open(full_path, "r") as f:
        return json.load(f)


def load_typos(file_path: str = "app/typos/typos.json") -> dict:
    # Resolve absolute path
    full_path = Path(file_path).resolve()
    if not full_path.exists():
        raise ValueError(f"Typos file {full_path} not found.")
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)



def normalize_city(city: str, mappings_file: str = "app/city_mappings/city_mappings.json") -> str:
    # Load city mappings
    city_mappings = load_city_mappings(mappings_file)

    # Normalize city name (strip spaces, title case)
    city = city.strip().title()

    # Map the city if it exists in the mappings, otherwise return the original
    return city_mappings.get(city, city)


def split_by_region(city: str, regions_file: str = "app/regions/regions.json") -> str:
    # Use the new `load_regions` with resolved path
    regions = load_regions(regions_file)

    # Normalize city name
    city = city.strip().title()

    # Find the region
    for region, cities in regions.items():
        if city in cities:
            return region
    return "Unknown"


def correct_typos(city: str, typos_file: str = "app/typos/typos.json") -> str:
    # Correct common city name typos based on data from a JSON file
    # Load typos data from the file
    typos = load_typos(typos_file)

    # Normalize the city name (strip spaces, title case)
    city = city.strip().title()

    # Return the corrected city name if a match is found, otherwise return the original city
    return typos.get(city, city)

