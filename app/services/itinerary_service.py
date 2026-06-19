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


def sorteaza_greedy(traseu, lat_start, lon_start):
    if not traseu:
        return []
    ramase = list(traseu)
    ordonate = []
    lat_cur, lon_cur = lat_start, lon_start
    while ramase:
        cea_mai_apropiata = min(
            ramase,
            key=lambda a: haversine(lat_cur, lon_cur, a.latitude, a.longitude)
        )
        ordonate.append(cea_mai_apropiata)
        lat_cur, lon_cur = cea_mai_apropiata.latitude, cea_mai_apropiata.longitude
        ramase.remove(cea_mai_apropiata)
    return ordonate


def fitness(
    traseu: list,
    lat_start: float,
    lon_start: float,
    timp_disponibil: int,
    zi_saptamana: int,
    ora_start: int,
    db: Session,
) -> float:
    if not traseu:
        return 0.0

    timp_total = 0
    lat_cur, lon_cur = lat_start, lon_start
    ora_curenta = ora_start
    scor = 0

    for a in traseu:
        timp_deplasare = haversine(lat_cur, lon_cur, a.latitude, a.longitude)
        timp_total += timp_deplasare
        ora_curenta += int(timp_deplasare)

        schedule = db.query(AttractionSchedule).filter(
            AttractionSchedule.id == a.id
        ).all()
        if not is_open(schedule, zi_saptamana, ora_curenta):
            return 0.0  # traseu invalid dacă o atracție e închisă

        visit = a.visit_time_min or 30
        timp_total += visit
        ora_curenta += visit

        if timp_total > timp_disponibil:
            return 0.0

        scor += 1 + (1 / (timp_deplasare + 1))  # mai multe atracții + distanță mică = mai bun
        lat_cur, lon_cur = a.latitude, a.longitude

    return scor


def genetic_itinerary(
    candidates: list,
    lat_start: float,
    lon_start: float,
    timp_disponibil: int,
    zi_saptamana: int,
    ora_start: int,
    db: Session,
    populatie: int = 50,
    generatii: int = 100,
) -> list:

    if not candidates:
        return []

    def individ_random():
        n = random.randint(1, min(len(candidates), 8))
        return random.sample(candidates, n)

    pop = [individ_random() for _ in range(populatie)]

    def evalueaza(ind):
        return fitness(ind, lat_start, lon_start, timp_disponibil, zi_saptamana, ora_start, db)

    for _ in range(generatii):

        scoruri = [(ind, evalueaza(ind)) for ind in pop]
        scoruri.sort(key=lambda x: x[1], reverse=True)


        supravietuitori = [ind for ind, _ in scoruri[:populatie // 2]]


        copii = []
        while len(copii) < populatie // 2:
            p1, p2 = random.sample(supravietuitori, 2)
            combined = list({a.id: a for a in p1 + p2}.values())
            n = random.randint(1, min(len(combined), 8))
            copil = random.sample(combined, n)
            copii.append(copil)


        for ind in copii:
            if random.random() < 0.1 and candidates:
                nou = random.choice(candidates)
                if nou not in ind:
                    ind.append(nou)

        pop = supravietuitori + copii

    best = max(pop, key=evalueaza)
    return best if evalueaza(best) > 0 else []


def build_itinerary(
    db: Session,
    categorii_preferate: list,
    buget_max: int,
    tip_spatiu: str | None,
    zi_saptamana: int,
    ora_start: int,
    cu_copii: bool,
    lat_start: float,
    lon_start: float,
    timp_disponibil: int,
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
            categorii_preferate=categorii_preferate,
            buget_max=buget_max,
            tip_spatiu=tip_spatiu,
            zi_saptamana=zi_saptamana,
            ora_start_minute=ora_start,
            cu_copii=cu_copii,
            user_id=user_id,
            top_n=20,
        )

    traseu = sorteaza_greedy(genetic_itinerary(
        candidates=candidates,
        lat_start=lat_start,
        lon_start=lon_start,
        timp_disponibil=timp_disponibil,
        zi_saptamana=zi_saptamana,
        ora_start=ora_start,
        db=db,
    ), lat_start, lon_start)


    timp_total = 0
    lat_cur, lon_cur = lat_start, lon_start
    stops = []
    ora_curenta = ora_start

    for a in traseu:
        timp_deplasare = haversine(lat_cur, lon_cur, a.latitude, a.longitude)
        timp_total += int(timp_deplasare)
        ora_curenta += int(timp_deplasare)

        visit = a.visit_time_min or 30
        timp_total += visit

        ore = ora_curenta // 60
        minute = ora_curenta % 60
        ora_str = f"{ore:02d}:{minute:02d}"

        stops.append({
            "attraction": a,
            "ora_vizita": ora_str,
            "durata_minute": visit,
            "timp_tranzit_minute": int(timp_deplasare),
        })

        ora_curenta += visit
        lat_cur, lon_cur = a.latitude, a.longitude

    return stops, timp_total

