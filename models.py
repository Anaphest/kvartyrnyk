from datetime import datetime
from sqlalchemy import (
    ForeignKey, String, Text, Boolean, DateTime, Table, Column,
    SmallInteger, CheckConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base



class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    address: Mapped[str | None] = mapped_column(String)
    city: Mapped[str] = mapped_column(String, default="Stockholm")
    map_url: Mapped[str | None] = mapped_column(String)
    
event_partners = Table(
    "event_partners", Base.metadata,
    Column("event_id", ForeignKey("events.id"), primary_key=True),
    Column("partner_id", ForeignKey("partners.id"), primary_key=True),
)

event_performers = Table(
    "event_performers", Base.metadata,
    Column("event_id", ForeignKey("events.id"), primary_key=True),
    Column("performer_id", ForeignKey("performers.id"), primary_key=True),
    Column("sort_order", SmallInteger, default=0),
)


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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "event_type IN ('concert','reading','open_mic','meeting','workshop','other')",
            name="events_event_type_check",
        ),
        CheckConstraint(
            "entry_type IN ('free','donation','ticket')",
            name="events_entry_type_check",
        ),
    )
    partners: Mapped[list["Partner"]] = relationship(secondary=event_partners)
    performers: Mapped[list["Performer"]] = relationship(
        secondary=event_performers,
        order_by=event_performers.c.sort_order,
    )

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




class Partner(Base):
    __tablename__ = "partners"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    logo_url: Mapped[str | None] = mapped_column(String)
    website: Mapped[str | None] = mapped_column(String)
    translations: Mapped[list["PartnerTranslation"]] = relationship(
        back_populates="partner", cascade="all, delete-orphan"
    )

class PartnerTranslation(Base):
    __tablename__ = "partner_translations"

    partner_id: Mapped[int] = mapped_column(
        ForeignKey("partners.id", ondelete="CASCADE"), primary_key=True
    )
    lang: Mapped[str] = mapped_column(String, primary_key=True)
    description: Mapped[str | None] = mapped_column(Text)

    partner: Mapped[Partner] = relationship(back_populates="translations")

class Performer(Base):
    __tablename__ = "performers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name_latin: Mapped[str] = mapped_column(String)
    name_uk: Mapped[str | None] = mapped_column(String)
    website: Mapped[str | None] = mapped_column(String)
    photo_url: Mapped[str | None] = mapped_column(String)
    translations: Mapped[list["PerformerTranslation"]] = relationship(
        back_populates="performer", cascade="all, delete-orphan"
    )

    def display_name(self, lang: str) -> str:
        return self.name_uk if lang == "uk" and self.name_uk else self.name_latin

class PerformerTranslation(Base):
    __tablename__ = "performer_translations"

    performer_id: Mapped[int] = mapped_column(
        ForeignKey("performers.id", ondelete="CASCADE"), primary_key=True
    )
    lang: Mapped[str] = mapped_column(String, primary_key=True)
    bio: Mapped[str | None] = mapped_column(Text)

    performer: Mapped[Performer] = relationship(back_populates="translations")


class EventLanguage(Base):
    __tablename__ = "event_languages"

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), primary_key=True
    )
    lang: Mapped[str] = mapped_column(String, primary_key=True)