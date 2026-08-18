from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base


class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    address: Mapped[str | None] = mapped_column(String)
    city: Mapped[str] = mapped_column(String, default="Stockholm")
    map_url: Mapped[str | None] = mapped_column(String)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String, unique=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    date_is_exact: Mapped[bool] = mapped_column(Boolean, default=True)
    venue_id: Mapped[int | None] = mapped_column(ForeignKey("venues.id"))
    event_type: Mapped[str] = mapped_column(String, default="concert")
    entry_type: Mapped[str] = mapped_column(String, default="donation")
    ticket_url: Mapped[str | None] = mapped_column(String)
    poster_url: Mapped[str | None] = mapped_column(String)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    venue: Mapped[Venue | None] = relationship()
    translations: Mapped[list["EventTranslation"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )


class EventTranslation(Base):
    __tablename__ = "event_translations"

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), primary_key=True)
    lang: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    fundraising_goal: Mapped[str | None] = mapped_column(Text)

    event: Mapped[Event] = relationship(back_populates="translations")