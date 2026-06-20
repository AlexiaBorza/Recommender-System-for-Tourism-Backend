import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.ai_loader import load_all_models
from app.database.connection import SessionLocal
from app.services.itinerary_service import build_itinerary


def setup_module(module):
    load_all_models()


def get_db_session():
    return SessionLocal()


def test_itinerariu_respecta_timpul_disponibil():
    db = get_db_session()
    try:
        stops, total_minutes = build_itinerary(
            db=db,
            preferred_categories=["park", "museum"],
            max_budget=2,
            space_type=None,
            weekday=5,
            start_time=540,
            lat_start=45.7489,
            lon_start=21.2087,
            available_time=240,
        )
        assert total_minutes <= 240
    finally:
        db.close()


def test_itinerariu_nu_are_duplicate():
    db = get_db_session()
    try:
        stops, total_minutes = build_itinerary(
            db=db,
            preferred_categories=["park", "museum", "restaurant"],
            max_budget=3,
            space_type=None,
            weekday=5,
            start_time=540,
            lat_start=45.7489,
            lon_start=21.2087,
            available_time=300,
        )
        ids = [s["attraction"].id for s in stops]
        assert len(ids) == len(set(ids))
    finally:
        db.close()


def test_itinerariu_cu_saved_attractions():
    db = get_db_session()
    try:
        stops, total_minutes = build_itinerary(
            db=db,
            preferred_categories=[],
            max_budget=3,
            space_type=None,
            weekday=5,
            start_time=540,
            lat_start=45.7489,
            lon_start=21.2087,
            available_time=300,
            saved_attraction_ids=[58417, 1250434],
        )
        assert len(stops) > 0
    finally:
        db.close()