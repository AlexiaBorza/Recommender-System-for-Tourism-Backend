import random
from sqlalchemy.orm import Session
from app.models.attraction_schedule import AttractionSchedule
from app.services.recommender import get_recommendations, is_open, hhmm_to_minutes
import math

def haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    dist_km = R * 2 * math.asin(math.sqrt(a))
    return (dist_km / 5) * 60


def greedy_sort(route, lat_start, lon_start):
    if not route:
        return []
    unvisited = list(route)
    ordered_route = []
    lat_cur, lon_cur = lat_start, lon_start
    while unvisited:
        closest_attraction = min(
            unvisited,
            key=lambda a: haversine(lat_cur, lon_cur, a.latitude, a.longitude)
        )
        ordered_route.append(closest_attraction)
        lat_cur, lon_cur = closest_attraction.latitude, closest_attraction.longitude
        unvisited.remove(closest_attraction)
    return ordered_route


def fitness(
    route: list,
    lat_start: float,
    lon_start: float,
    available_time: int,
    weekday: int,
    start_time: int,
    db: Session,
) -> float:
    if not route:
        return 0.0

    total_time = 0
    lat_cur, lon_cur = lat_start, lon_start
    current_time = start_time
    fitness_score = 0

    for a in route:
        travel_time = haversine(lat_cur, lon_cur, a.latitude, a.longitude)
        total_time += travel_time
        current_time += int(travel_time)

        schedule = db.query(AttractionSchedule).filter(
            AttractionSchedule.id == a.id
        ).all()
        if not is_open(schedule, weekday, current_time):
            return 0.0  # traseu invalid dacă o atracție e închisă

        visit = a.visit_time_min or 30
        total_time += visit
        current_time += visit

        if total_time > available_time:
            return 0.0

        fitness_score += 1 + (1 / (travel_time + 1))
        lat_cur, lon_cur = a.latitude, a.longitude

    return fitness_score


def genetic_itinerary(
    candidates: list,
    lat_start: float,
    lon_start: float,
    available_time: int,
    weekday: int,
    start_time: int,
    db: Session,
    population_size: int = 50,
    generation_count: int = 100,
) -> list:

    if not candidates:
        return []

    def random_individual():
        n = random.randint(1, min(len(candidates), 8))
        return random.sample(candidates, n)

    pop = [random_individual() for _ in range(population_size)]

    def evaluate_fitness(ind):
        return fitness(ind, lat_start, lon_start, available_time, weekday, start_time, db)

    for _ in range(generation_count):

        scored_population = [(ind, evaluate_fitness(ind)) for ind in pop]
        scored_population.sort(key=lambda x: x[1], reverse=True)

        survivors = [ind for ind, _ in scored_population[:population_size // 2]]

        offspring = []
        while len(offspring) < population_size // 2:
            p1, p2 = random.sample(survivors, 2)
            combined = list({a.id: a for a in p1 + p2}.values())
            n = random.randint(1, min(len(combined), 8))
            child_individual = random.sample(combined, n)
            offspring.append(child_individual)

        for ind in offspring:
            if random.random() < 0.1 and candidates:
                new_attraction = random.choice(candidates)
                if new_attraction not in ind:
                    ind.append(new_attraction)

        pop = survivors + offspring

    best = max(pop, key=evaluate_fitness)
    return best if evaluate_fitness(best) > 0 else []


def build_itinerary(
    db: Session,
    preferred_categories: list,
    max_budget: int,
    space_type: str | None,
    weekday: int,
    start_time: int,
    lat_start: float,
    lon_start: float,
    available_time: int,
    user_id: int | None = None,
    saved_attraction_ids: list = [],
) -> tuple:

    if saved_attraction_ids:
        from app.models.attractions import Attraction
        candidates = db.query(Attraction).filter(
            Attraction.id.in_(saved_attraction_ids)
        ).all()
    else:
        candidates = get_recommendations(
            db=db,
            preferred_categories=preferred_categories,
            max_budget=max_budget,
            space_type=space_type,
            weekday=weekday,
            start_time_minute=start_time,
            user_id=user_id,
            top_n=20,
        )

    route = greedy_sort(genetic_itinerary(
        candidates=candidates,
        lat_start=lat_start,
        lon_start=lon_start,
        available_time=available_time,
        weekday=weekday,
        start_time=start_time,
        db=db,
    ), lat_start, lon_start)

    total_time = 0
    lat_cur, lon_cur = lat_start, lon_start
    stops = []
    current_time = start_time

    for a in route:
        travel_time = haversine(lat_cur, lon_cur, a.latitude, a.longitude)
        total_time += int(travel_time)
        current_time += int(travel_time)

        visit = a.visit_time_min or 30
        total_time += visit

        hours = current_time // 60
        minutes = current_time % 60
        time_str = f"{hours:02d}:{minutes:02d}"

        stops.append({
            "attraction": a,
            "ora_vizita": time_str,
            "durata_minute": visit,
            "timp_tranzit_minute": int(travel_time),
        })

        current_time += visit
        lat_cur, lon_cur = a.latitude, a.longitude

    return stops, total_time