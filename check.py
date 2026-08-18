from sqlalchemy import select
from db import SessionLocal
from models import Event

with SessionLocal() as session:
    events = session.scalars(select(Event)).all()
    print(f"Подій у базі: {len(events)}")