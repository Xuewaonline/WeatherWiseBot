"""
WeatherWiseBot Rule-Based Clothing Recommendation Engine

Rules are based on temperature ranges, rain chance, wind speed, and weather conditions.
"""


def get_clothing_recommendation(temperature, rain_chance, wind_speed, description=""):
    """
    Generate clothing recommendation based on weather conditions.

    Args:
        temperature: Current temperature in Celsius
        rain_chance: Rain probability (0-100)
        wind_speed: Wind speed in m/s
        description: Weather description string

    Returns:
        dict with recommendation details
    """
    desc_lower = description.lower() if description else ""
    layers = []
    accessories = []
    footwear = ""
    special_notes = []

    # --- Temperature-based clothing ---
    if temperature >= 35:
        layers = ["Light cotton t-shirt or linen top", "Shorts or breathable skirt"]
        footwear = "Sandals or breathable sneakers"
        special_notes.append("Extreme heat! Stay hydrated and wear sunscreen.")
    elif temperature >= 28:
        layers = ["Light t-shirt or polo shirt", "Shorts or light trousers"]
        footwear = "Sneakers or breathable shoes"
        special_notes.append("Hot weather. Choose light-colored, breathable fabrics.")
    elif temperature >= 22:
        layers = ["T-shirt or light blouse", "Light trousers or jeans"]
        footwear = "Comfortable sneakers"
    elif temperature >= 15:
        layers = ["Long-sleeve shirt or light sweater", "Jeans or casual trousers"]
        footwear = "Sneakers or casual shoes"
        accessories.append("Light jacket for evenings")
    elif temperature >= 10:
        layers = ["Warm sweater or fleece", "Trousers"]
        footwear = "Closed shoes or boots"
        accessories.append("Light coat or windbreaker")
    elif temperature >= 5:
        layers = ["Thermal base layer", "Warm sweater", "Winter coat"]
        footwear = "Warm boots"
        accessories.extend(["Scarf", "Gloves"])
    elif temperature >= 0:
        layers = ["Thermal underwear", "Thick wool sweater", "Heavy winter coat"]
        footwear = "Insulated waterproof boots"
        accessories.extend(["Warm scarf", "Insulated gloves", "Warm hat"])
        special_notes.append("Near freezing! Dress in multiple layers.")
    else:
        layers = ["Thermal base layer", "Fleece mid-layer", "Heavy down jacket"]
        footwear = "Insulated snow boots"
        accessories.extend(["Thermal scarf", "Insulated gloves", "Thermal hat", "Hand warmers"])
        special_notes.append("Extreme cold! Minimize exposed skin. Risk of frostbite.")

    # --- Rain adjustments ---
    if rain_chance >= 70:
        accessories.append("Umbrella (high rain chance)")
        footwear = "Waterproof boots" if temperature < 15 else "Waterproof shoes"
        layers[-1] = layers[-1] + " (waterproof preferred)"
        special_notes.append("Heavy rain likely. Carry a sturdy umbrella.")
    elif rain_chance >= 40:
        accessories.append("Compact umbrella")
        special_notes.append("Moderate rain chance. Pack a rain cover.")
    elif rain_chance >= 20:
        accessories.append("Foldable umbrella just in case")

    # --- Wind adjustments ---
    if wind_speed > 15:
        if "coat" not in " ".join(layers).lower():
            accessories.append("Windproof jacket")
        special_notes.append("Very windy! Secure loose clothing and accessories.")
    elif wind_speed > 8:
        if temperature < 20:
            accessories.append("Windbreaker or layered jacket")
        special_notes.append("Breezy conditions. A wind-resistant layer helps.")

    # --- Weather condition adjustments ---
    if "snow" in desc_lower:
        footwear = "Waterproof snow boots with good grip"
        if "Thermal" not in " ".join(layers):
            layers.insert(0, "Thermal base layer")
        special_notes.append("Snowy conditions. Watch for slippery surfaces.")

    if "thunderstorm" in desc_lower:
        special_notes.append("Thunderstorm expected. Stay indoors if possible.")

    if "fog" in desc_lower or "mist" in desc_lower:
        special_notes.append("Low visibility. Wear bright or reflective clothing if walking/cycling.")

    # --- Sun protection for clear/hot days ---
    if temperature >= 25 and ("clear" in desc_lower or "sun" in desc_lower):
        accessories.append("Sunglasses")
        accessories.append("Sun hat or cap")
        special_notes.append("Sunny day. Apply SPF 30+ sunscreen.")

    # Build suggestion text
    suggestion_parts = []
    suggestion_parts.append(f"Wear {', '.join(layers)}.")
    suggestion_parts.append(f"Footwear: {footwear}.")
    if accessories:
        suggestion_parts.append(f"Bring: {', '.join(accessories)}.")
    if special_notes:
        suggestion_parts.append(" ".join(special_notes))

    return {
        "temperature": temperature,
        "rain_chance": rain_chance,
        "wind_speed": wind_speed,
        "layers": layers,
        "footwear": footwear,
        "accessories": accessories,
        "special_notes": special_notes,
        "suggestion": " ".join(suggestion_parts),
    }


def get_event_clothing(origin_weather, destination_weather, event_type="Flight"):
    """
    Generate clothing recommendation for travel events considering both cities.

    Args:
        origin_weather: dict with temp, rain_chance, wind_speed, description for origin
        destination_weather: dict with same fields for destination

    Returns:
        Combined recommendation string
    """
    origin_rec = get_clothing_recommendation(
        origin_weather["temperature"],
        origin_weather.get("rain_chance", 0),
        origin_weather.get("wind_speed", 0),
        origin_weather.get("description", ""),
    )
    dest_rec = get_clothing_recommendation(
        destination_weather["temperature"],
        destination_weather.get("rain_chance", 0),
        destination_weather.get("wind_speed", 0),
        destination_weather.get("description", ""),
    )

    temp_diff = abs(origin_weather["temperature"] - destination_weather["temperature"])

    lines = []
    lines.append(f"[{event_type} Outfit Guide]")
    lines.append(f"Origin ({origin_weather.get('city', 'Origin')}): {origin_weather['temperature']}C, {origin_weather.get('description', '')}")
    lines.append(f"Destination ({destination_weather.get('city', 'Dest')}): {destination_weather['temperature']}C, {destination_weather.get('description', '')}")
    lines.append("")

    if temp_diff > 10:
        lines.append(f"Large temperature difference ({temp_diff:.0f}C)! Dress in removable layers.")
        # Use the colder city's recommendation as base
        if origin_weather["temperature"] < destination_weather["temperature"]:
            lines.append(f"Base outfit for {origin_weather.get('city', 'Origin')}: {origin_rec['suggestion']}")
            lines.append(f"Pack lighter clothes for {destination_weather.get('city', 'Dest')}.")
        else:
            lines.append(f"Base outfit for {destination_weather.get('city', 'Dest')}: {dest_rec['suggestion']}")
            lines.append(f"You can dress lighter at {origin_weather.get('city', 'Origin')}.")
    else:
        lines.append(f"Similar weather at both cities. {origin_rec['suggestion']}")

    # Combine accessories from both
    all_acc = set(origin_rec["accessories"] + dest_rec["accessories"])
    if all_acc:
        lines.append(f"Recommended accessories: {', '.join(all_acc)}.")

    # Combined notes
    all_notes = set(origin_rec["special_notes"] + dest_rec["special_notes"])
    if all_notes:
        lines.append("Notes: " + " ".join(all_notes))

    return "\n".join(lines)
