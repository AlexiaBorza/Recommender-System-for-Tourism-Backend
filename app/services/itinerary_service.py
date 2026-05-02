def build_itinerary(attractions, available_minutes: int):
    selected = []
    total = 0

    for attraction in attractions:
        visit_time = attraction.estimated_visit_time or 30

        if total + visit_time <= available_minutes:
            selected.append(attraction)
            total += visit_time

    return selected, total