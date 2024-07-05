def generate_location_tips(location_counts):
    """
    Generate tips based on the location counts.
    """
    tips = []
    for location, count in location_counts.items():
        tips.append(f"{location}: {count} listings")
    return "\n".join(tips)

def generate_item_description(detailed_items):
    """
    Generate a description for the detailed items.
    """
    descriptions = []
    for item in detailed_items:
        descriptions.append(f"Title: {item['title']}, Price: £{item['price_gbp']:.2f}, Condition: {item['condition']}, Grade: {item['grade']}, Location: {item['location']}")
    return "\n".join(descriptions)
