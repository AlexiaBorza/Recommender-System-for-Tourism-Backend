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
            categorii_preferate=["park"],
            buget_max=2,
            tip_spatiu=None,
            zi_saptamana=5,
            ora_start_minute=600,
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
            categorii_preferate=["museum"],
            buget_max=3,
            tip_spatiu=None,
            zi_saptamana=5,
            ora_start_minute=600,
            top_n=10,
        )
        # toate rezultatele trebuie să fie din categoria ceruta
        for atractie in rezultate:
            assert atractie.category == "museum"
    finally:
        db.close()


def test_recomandari_respecta_bugetul():
    db = get_db_session()
    try:
        rezultate = get_recommendations(
            db=db,
            categorii_preferate=["restaurant", "cafe"],
            buget_max=1,
            tip_spatiu=None,
            zi_saptamana=5,
            ora_start_minute=600,
            top_n=20,
        )
        for atractie in rezultate:
            assert atractie.range_pret <= 1
    finally:
        db.close()