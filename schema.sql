-- Kvartyrnyk — schema v1 (events layer)
-- PostgreSQL

-- ---------- reference data ----------

CREATE TABLE venues (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    address     TEXT,
    city        TEXT NOT NULL DEFAULT 'Stockholm',
    map_url     TEXT
);

CREATE TABLE partners (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    logo_url    TEXT,
    website     TEXT
);

CREATE TABLE partner_translations (
    partner_id  INTEGER NOT NULL REFERENCES partners(id) ON DELETE CASCADE,
    lang        TEXT NOT NULL CHECK (lang IN ('uk', 'en', 'sv')),
    description TEXT,
    PRIMARY KEY (partner_id, lang)
);

CREATE TABLE performers (
    id          SERIAL PRIMARY KEY,
    name_latin  TEXT NOT NULL,   -- as in passport / as the artist spells it
    name_uk     TEXT,            -- Cyrillic form, if any
    website     TEXT,
    photo_url   TEXT
);

CREATE TABLE performer_translations (
    performer_id INTEGER NOT NULL REFERENCES performers(id) ON DELETE CASCADE,
    lang         TEXT NOT NULL CHECK (lang IN ('uk', 'en', 'sv')),
    bio          TEXT,
    PRIMARY KEY (performer_id, lang)
);

-- ---------- events ----------

CREATE TABLE events (
    id            SERIAL PRIMARY KEY,
    slug          TEXT NOT NULL UNIQUE,        -- for URLs: /en/event/bandura-girl-2026
    starts_at     TIMESTAMPTZ NOT NULL,
    ends_at       TIMESTAMPTZ,
    date_is_exact BOOLEAN NOT NULL DEFAULT TRUE,   -- false = "sometime in September"
    venue_id      INTEGER REFERENCES venues(id),   -- nullable: venue may be TBA
    event_type    TEXT NOT NULL DEFAULT 'concert'
                  CHECK (event_type IN ('concert', 'reading', 'open_mic',
                                        'meeting', 'workshop', 'other')),
    entry_type    TEXT NOT NULL DEFAULT 'donation'
                  CHECK (entry_type IN ('free', 'donation', 'ticket')),
    ticket_url    TEXT,
    poster_url    TEXT,
    is_published  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_events_starts_at ON events (starts_at);
CREATE INDEX idx_events_published ON events (is_published, starts_at);

CREATE TABLE event_translations (
    event_id         INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    lang             TEXT NOT NULL CHECK (lang IN ('uk', 'en', 'sv')),
    title            TEXT NOT NULL,
    description      TEXT,
    fundraising_goal TEXT,   -- "vehicle for a UAV unit", null if not a fundraiser
    PRIMARY KEY (event_id, lang)
);

-- languages the event itself is held in (can be several)
CREATE TABLE event_languages (
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    lang     TEXT NOT NULL CHECK (lang IN ('uk', 'en', 'sv', 'other')),
    PRIMARY KEY (event_id, lang)
);

CREATE TABLE event_partners (
    event_id   INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    partner_id INTEGER NOT NULL REFERENCES partners(id) ON DELETE CASCADE,
    PRIMARY KEY (event_id, partner_id)
);

CREATE TABLE event_performers (
    event_id     INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    performer_id INTEGER NOT NULL REFERENCES performers(id) ON DELETE CASCADE,
    sort_order   SMALLINT NOT NULL DEFAULT 0,
    PRIMARY KEY (event_id, performer_id)
);
