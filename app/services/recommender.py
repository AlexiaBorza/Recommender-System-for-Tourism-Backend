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


def is_open(schedule_rows, weekday: int, start_time: int) -> bool:
    for row in schedule_rows:
        if row.zi == weekday:
            opens_at = hhmm_to_minutes(row.ora_deschidere)
            closes_at = hhmm_to_minutes(row.ora_inchidere)
            if row.ora_inchidere == 0:
                return True
            return opens_at <= start_time < closes_at
    return False


def get_recommendations(
    db: Session,
    preferred_categories: list,
    max_budget: int,
    space_type: str | None,
    weekday: int,
    start_time_minute: int,
    user_id: int | None = None,
    top_n: int = 10,
) -> list:
    cosine_data = get_cosine_model()
    svd_data = get_svd_model()

    tfidf = cosine_data["tfidf_vectorizer"]
    tfidf_matrix = cosine_data["tfidf_matrix"]
    df_cosine = cosine_data["dataframe"]
    category_tags = cosine_data["category_tags"]
    space_tags = cosine_data["spatiu_tags"]
    price_tags = cosine_data["pret_tags"]

    # Profil utilizator → vector TF-IDF
    profile_tags = [category_tags.get(cat, cat) for cat in preferred_categories]
    if space_type:
        profile_tags.append(space_tags.get(space_type, ""))
    profile_tags.append(price_tags.get(max_budget, ""))

    profile_vector = tfidf.transform([" ".join(profile_tags)])

    from sklearn.metrics.pairwise import cosine_similarity
    cosine_scores = cosine_similarity(profile_vector, tfidf_matrix).flatten()

    # Scor SVD
    svd_scores = {}
    if user_id and user_id in svd_data["user_idx"]:
        u = svd_data["user_idx"][user_id]
        predicted = svd_data["predicted_ratings"]
        for loc_id, i in svd_data["item_idx"].items():
            svd_scores[loc_id] = float(predicted[u, i])

    # Filtre din DB
    query = db.query(Attraction).filter(
        Attraction.range_pret <= max_budget,
        Attraction.category.in_(preferred_categories)
    )

    if space_type:
        query = query.filter(Attraction.tip_spatiu == space_type)

    attractions = query.all()

    open_attractions = []
    for a in attractions:
        schedule = db.query(AttractionSchedule).filter(
            AttractionSchedule.id == a.id
        ).all()
        if is_open(schedule, weekday, start_time_minute):
            open_attractions.append(a)

    id_to_idx = {int(df_cosine.iloc[i]["id"]): i for i in range(len(df_cosine))}

    results = []
    for a in open_attractions:
        idx = id_to_idx.get(a.id)
        cosine_score = float(cosine_scores[idx]) if idx is not None else 0.0
        sentiment_score = get_sentiment_score(a.id, db)

        if svd_scores:
            svd_score = svd_scores.get(a.id, cosine_score)
            final_score = 0.5 * cosine_score + 0.3 * (svd_score / 5.0) + 0.2 * (sentiment_score / 5.0)
        else:
            final_score = 0.8 * cosine_score + 0.2 * (sentiment_score / 5.0)

        results.append((a, final_score))

    results.sort(key=lambda x: x[1], reverse=True)
    return [a for a, _ in results[:top_n]]