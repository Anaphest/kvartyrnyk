from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from db import get_session
from models import Event, EventTranslation
from fastapi.staticfiles import StaticFiles

from datetime import datetime, timezone

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Stockholm")
MONTHS = {
    "uk": ["січень", "лютий", "березень", "квітень", "травень", "червень",
           "липень", "серпень", "вересень", "жовтень", "листопад", "грудень"],
    "en": ["January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"],
    "sv": ["januari", "februari", "mars", "april", "maj", "juni",
           "juli", "augusti", "september", "oktober", "november", "december"],
}

def _local(value):
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(TZ)


def dt(value, fmt="%d.%m.%Y, %H:%M"):
    if value is None:
        return ""
    return _local(value).strftime(fmt)


def month_year(value, lang="uk"):
    if value is None:
        return ""
    v = _local(value)
    return f"{MONTHS.get(lang, MONTHS['en'])[v.month - 1]} {v.year}"


templates.env.filters["dt"] = dt
templates.env.filters["month_year"] = month_year


LANGS = ("uk", "en", "sv")
FALLBACK = {"uk": ["uk", "en"], "en": ["en", "uk"], "sv": ["sv", "en", "uk"]}


def pick(translations, lang):
    by_lang = {t.lang: t for t in translations}
    for candidate in FALLBACK[lang]:
        if candidate in by_lang:
            return by_lang[candidate]
    # останній рубіж: будь-який наявний переклад краще, ніж 500
    return next(iter(by_lang.values()), None)

@app.get("/")
def root():
    return RedirectResponse("/uk/")


@app.get("/{lang}/")
def home(lang: str, request: Request, session: Session = Depends(get_session)):
    if lang not in LANGS:
        raise HTTPException(status_code=404)

    now = datetime.now(timezone.utc)
    opts = (selectinload(Event.translations), selectinload(Event.venue))

    upcoming = session.scalars(
        select(Event)
        .where(Event.is_published, Event.starts_at >= now)
        .order_by(Event.starts_at)
        .options(*opts)
    ).all()

    past = session.scalars(
        select(Event)
        .where(Event.is_published, Event.starts_at < now)
        .order_by(Event.starts_at.desc())
        .limit(6)
        .options(*opts)
    ).all()

    return templates.TemplateResponse(
        request=request, name="index.html",
        context={
            "lang": lang,
            "upcoming": [(e, t) for e in upcoming if (t := pick(e.translations, lang))],
            "past": [(e, t) for e in past if (t := pick(e.translations, lang))],
        },
    )

@app.get("/{lang}/event/{slug}")
def event_page(lang: str, slug: str, request: Request,
               session: Session = Depends(get_session)):
    if lang not in LANGS:
        raise HTTPException(status_code=404)

    event = session.scalar(
        select(Event)
        .where(Event.slug == slug, Event.is_published)
        .options(
            selectinload(Event.translations),
            selectinload(Event.venue),
            selectinload(Event.partners),
            selectinload(Event.performers),
        )
    )
    if event is None:
        raise HTTPException(status_code=404)

    t = pick(event.translations, lang)
    if t is None:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        request=request, name="event.html",
        context={"event": event, "t": t, "lang": lang},
    )
