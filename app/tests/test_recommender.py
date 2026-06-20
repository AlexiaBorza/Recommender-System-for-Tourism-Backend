import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.ai_loader import load_all_models
from app.database.connection import SessionLocal
from app.services.recommender import get_recommendations


def setup_module(module):
    load_all_models()


def get_db_session():
    return SessionLocal()


def test_recomandari_returneaza_rezultate():
    db = get_db_session()
    try:
        rezultate = get_recommendations(
            db=db,
            preferred_categories=["park"],
            max_budget=2,
            space_type=None,
            weekday=5,
            start_time_minute=600,
            top_n=10,
        )
        assert len(rezultate) > 0
    finally:
        db.close()


def test_recomandari_respecta_categoria():
    db = get_db_session()
    try:
        rezultate = get_recommendations(
            db=db,
            preferred_categories=["museum"],
            max_budget=3,
            space_type=None,
            weekday=5,
            start_time_minute=600,
            top_n=10,
        )
        for atractie in rezultate:
            assert atractie.category == "museum"
    finally:
        db.close()


def test_recomandari_respecta_bugetul():
    db = get_db_session()
    try:
        rezultate = get_recommendations(
            db=db,
            preferred_categories=["restaurant", "cafe"],
            max_budget=1,
            space_type=None,
            weekday=5,
            start_time_minute=600,
            top_n=20,
        )
        for atractie in rezultate:
            assert atractie.range_pret <= 1
    finally:
        db.close()