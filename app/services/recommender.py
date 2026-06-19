import numpy as np
from sqlalchemy.orm import Session
from app.services.ai_loader import get_cosine_model, get_svd_model
from app.models.attractions import Attraction
from app.models.attraction_schedule import AttractionSchedule
from app.services.sentiment_service import get_sentiment_score

def hhmm_to_minutes(hhmm: int) -> int:
    if hhmm == 0:
        return 0
    if hhmm == 2400:
        return 1440
    return (hhmm // 100) * 60 + (hhmm % 100)


def is_open(schedule_rows, zi: int, ora_start: int) -> bool:
    for row in schedule_rows:
        if row.zi == zi:
            deschide = hhmm_to_minutes(row.ora_deschidere)
            inchide  = hhmm_to_minutes(row.ora_inchidere)
            if row.ora_inchidere == 0:
                return True
            return deschide <= ora_start < inchide
    return False



def get_recommendations(
    db: Session,
    categorii_preferate: list,
    buget_max: int,
    tip_spatiu: str | None,
    zi_saptamana: int,
    ora_start_minute: int,
    cu_copii: bool = False,
    user_id: int | None = None,
    top_n: int = 10,
) -> list:
    cosine_data = get_cosine_model()
    svd_data = get_svd_model()

    tfidf = cosine_data["tfidf_vectorizer"]
    tfidf_matrix = cosine_data["tfidf_matrix"]
    df_cosine = cosine_data["dataframe"]
    category_tags = cosine_data["category_tags"]
    spatiu_tags = cosine_data["spatiu_tags"]
    pret_tags = cosine_data["pret_tags"]

    # Profil utilizator → vector TF-IDF
    profil_tags = [category_tags.get(cat, cat) for cat in categorii_preferate]
    if tip_spatiu:
        profil_tags.append(spatiu_tags.get(tip_spatiu, ""))
    profil_tags.append(pret_tags.get(buget_max, ""))

    profil_vector = tfidf.transform([" ".join(profil_tags)])

    from sklearn.metrics.pairwise import cosine_similarity
    scoruri_cosine = cosine_similarity(profil_vector, tfidf_matrix).flatten()

    # Scor SVD
    svd_scores = {}
    print(f"[SVD] User {user_id} in model: {user_id in svd_data['user_idx']}")
    print(f"[SVD] Nr useri in model: {len(svd_data['user_idx'])}")
    print(f"[SVD] Nr atractii in model: {len(svd_data['item_idx'])}")
    if user_id and user_id in svd_data["user_idx"]:
        u = svd_data["user_idx"][user_id]
        predicted = svd_data["predicted_ratings"]
        for loc_id, i in svd_data["item_idx"].items():
            svd_scores[loc_id] = float(predicted[u, i])



    # Filtre din DB
    query = db.query(Attraction).filter(
        Attraction.range_pret <= buget_max,
        Attraction.category.in_(categorii_preferate)
    )

    if tip_spatiu:
        query = query.filter(Attraction.tip_spatiu == tip_spatiu)

    if cu_copii:
        query = query.filter(
            Attraction.category.notin_(["pub", "bar", "nightclub"])
        )

    attractions = query.all()

    # Filtru orar
    attractions_deschise = []
    for a in attractions:
        schedule = db.query(AttractionSchedule).filter(
            AttractionSchedule.id == a.id
        ).all()
        if is_open(schedule, zi_saptamana, ora_start_minute):
            attractions_deschise.append(a)

    # Scor final hibrid
    id_to_idx = {int(df_cosine.iloc[i]["id"]): i for i in range(len(df_cosine))}

    rezultate = []
    for a in attractions_deschise:
        idx = id_to_idx.get(a.id)
        cosine_score = float(scoruri_cosine[idx]) if idx is not None else 0.0
        sentiment_score = get_sentiment_score(a.id, db)

        if svd_scores:
            svd_score = svd_scores.get(a.id, cosine_score)
            scor_final = 0.5 * cosine_score + 0.3 * (svd_score / 5.0) + 0.2 * (sentiment_score / 5.0)
        else:
            scor_final = 0.8 * cosine_score + 0.2 * (sentiment_score / 5.0)

        rezultate.append((a, scor_final))

    rezultate.sort(key=lambda x: x[1], reverse=True)
    return [a for a, _ in rezultate[:top_n]]

