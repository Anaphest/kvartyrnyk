from datetime import datetime
from sqlalchemy import (
    ForeignKey, Text, Boolean, DateTime, Table, Column,
    SmallInteger, CheckConstraint, Index, func, text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base



class Venue(Base):
    __tablename__ = "venues"
   
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    address: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str] = mapped_column(Text, default="Stockholm")
    map_url: Mapped[str | None] = mapped_column(Text)
    
event_partners = Table(
    "event_partners", Base.metadata,
    Column("event_id", ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
    Column("partner_id", ForeignKey("partners.id", ondelete="CASCADE"), primary_key=True),
)


event_performers = Table(
    "event_performers", Base.metadata,
    Column("event_id", ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
    Column("performer_id", ForeignKey("performers.id", ondelete="CASCADE"), primary_key=True),
    Column("sort_order", SmallInteger, nullable=False, server_default=text("0")),
)



class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(Text, unique=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    date_is_exact: Mapped[bool] = mapped_column(Boolean, default=True)
    venue_id: Mapped[int | None] = mapped_column(ForeignKey("venues.id"))
    event_type: Mapped[str] = mapped_column(Text, default="concert")
    entry_type: Mapped[str] = mapped_column(Text, default="donation")
    ticket_url: Mapped[str | None] = mapped_column(Text)
    poster_url: Mapped[str | None] = mapped_column(Text)
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
        Index("idx_events_starts_at", "starts_at"),
        Index("idx_events_published", "is_published", "starts_at"),
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

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), primary_key=True
    )
    lang: Mapped[str] = mapped_column(Text, primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    fundraising_goal: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (
        CheckConstraint("lang IN ('uk','en','sv')",
                        name="event_translations_lang_check"),
    )

    event: Mapped[Event] = relationship(back_populates="translations")
    




class Partner(Base):
    __tablename__ = "partners"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    logo_url: Mapped[str | None] = mapped_column(Text)
    website: Mapped[str | None] = mapped_column(Text)
    translations: Mapped[list["PartnerTranslation"]] = relationship(
        back_populates="partner", cascade="all, delete-orphan"
    )

class PartnerTranslation(Base):
    __tablename__ = "partner_translations"

    partner_id: Mapped[int] = mapped_column(
        ForeignKey("partners.id", ondelete="CASCADE"), primary_key=True
    )
    lang: Mapped[str] = mapped_column(Text, primary_key=True)
    description: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (
        CheckConstraint("lang IN ('uk','en','sv')",
                        name="partner_translations_lang_check"),
    )

    partner: Mapped[Partner] = relationship(back_populates="translations")

class Performer(Base):
    __tablename__ = "performers"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str | None] = mapped_column(Text, unique=True)
    name_latin: Mapped[str] = mapped_column(Text)
    name_uk: Mapped[str | None] = mapped_column(Text)
    website: Mapped[str | None] = mapped_column(Text)
    photo_url: Mapped[str | None] = mapped_column(Text)
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
    lang: Mapped[str] = mapped_column(Text, primary_key=True)
    bio: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (
        CheckConstraint("lang IN ('uk','en','sv')",
                        name="performer_translations_lang_check"),
    )

    performer: Mapped[Performer] = relationship(back_populates="translations")


class EventLanguage(Base):
    __tablename__ = "event_languages"

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), primary_key=True
    )
    lang: Mapped[str] = mapped_column(Text, primary_key=True)

    __table_args__ = (
        CheckConstraint("lang IN ('uk','en','sv','other')",
                        name="event_languages_lang_check"),
    )

class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(Text, unique=True)
    sort_order: Mapped[int] = mapped_column(SmallInteger, nullable=False,
                                            server_default=text("0"))

    translations: Mapped[list["GenreTranslation"]] = relationship(
        back_populates="genre", cascade="all, delete-orphan"
    )

    def name(self, lang: str) -> str:
        by_lang = {t.lang: t.name for t in self.translations}
        for candidate in (lang, "en", "uk"):
            if candidate in by_lang:
                return by_lang[candidate]
        return self.code


class GenreTranslation(Base):
    __tablename__ = "genre_translations"

    genre_id: Mapped[int] = mapped_column(
        ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True
    )
    lang: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint("lang IN ('uk','en','sv')",
                        name="genre_translations_lang_check"),
    )

    genre: Mapped[Genre] = relationship(back_populates="translations")

class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_latin: Mapped[str] = mapped_column(Text)
    author_uk: Mapped[str | None] = mapped_column(Text)
    title_original: Mapped[str] = mapped_column(Text)
    lang: Mapped[str] = mapped_column(Text)
    isbn: Mapped[str | None] = mapped_column(Text)
    year: Mapped[int | None] = mapped_column(SmallInteger)
    audience: Mapped[str] = mapped_column(Text, server_default=text("'adult'"))
    war_related: Mapped[bool] = mapped_column(Boolean, nullable=False,
                                              server_default=text("false"))
    cover_url: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    translations: Mapped[list["BookTranslation"]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("lang IN ('uk','en','sv','other')", name="books_lang_check"),
        CheckConstraint("audience IN ('adult','teen','child')",
                        name="books_audience_check"),
        Index("idx_books_author", "author_latin"),
    )

    def author_name(self, lang: str) -> str:
        return self.author_uk if lang == "uk" and self.author_uk else self.author_latin

class BookTranslation(Base):
    __tablename__ = "book_translations"

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), primary_key=True
    )
    lang: Mapped[str] = mapped_column(Text, primary_key=True)
    title: Mapped[str | None] = mapped_column(Text)
    annotation: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint("lang IN ('uk','en','sv')",
                        name="book_translations_lang_check"),
    )

    book: Mapped[Book] = relationship(back_populates="translations")

    