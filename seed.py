from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from db import SessionLocal
from models import Venue, Event, EventTranslation

STOCKHOLM = timezone(timedelta(hours=2))  # CEST

with SessionLocal() as session:
    venue = session.scalar(
        select(Venue).where(Venue.name == "Stockholms Improvisationsteater")
    )
    if venue is None:
        venue = Venue(
            name="Stockholms Improvisationsteater",
            address="Sigtunagatan 12",
            city="Stockholm",
        )
        session.add(venue)

    event = Event(
        slug="banduragirl-2026",
        starts_at=datetime(2026, 8, 9, 16, 0, tzinfo=STOCKHOLM),
        venue=venue,
        event_type="concert",
        entry_type="donation",
        is_published=True,
    )

    event.translations.append(EventTranslation(
        lang="uk",
        title="BanduraGirl — Wings for Ukraine",
        description=(
            "BanduraGirl (Анастасія Войтюк) поєднує українську музичну "
            "традицію з world music, джазом, інді та електронною музикою. "
            "У її концертах архаїка зустрічається із сучасністю."
        ),
        fundraising_goal="Автомобіль для підрозділу БпЛА",
    ))

    event.translations.append(EventTranslation(
        lang="en",
        title="BanduraGirl — Wings for Ukraine",
        description=(
            "BanduraGirl (Anastasiya Voytyuk) blends Ukrainian musical "
            "traditions with world music, jazz, indie and electronics. "
            "In her performances, ancient roots meet contemporary sound."
        ),
        fundraising_goal="A vehicle for a UAV unit",
    ))

    session.add(event)
    session.commit()
    print(f"Створено подію id={event.id}")