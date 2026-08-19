from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from db import get_session
from models import Event, EventTranslation

app = FastAPI()
templates = Jinja2Templates(directory="templates")

LANGS = ("uk", "en", "sv")
FALLBACK = {"uk": ["uk", "en"], "en": ["en", "uk"], "sv": ["sv", "en", "uk"]}


def pick(translations, lang):
    by_lang = {t.lang: t for t in translations}
    for candidate in FALLBACK[lang]:
        if candidate in by_lang:
            return by_lang[candidate]
    return None


@app.get("/")
def root():
    return RedirectResponse("/uk/")


@app.get("/{lang}/")
def home(lang: str, request: Request, session: Session = Depends(get_session)):
    if lang not in LANGS:
        raise HTTPException(status_code=404)

    events = session.scalars(
        select(Event)
        .where(Event.is_published)
        .order_by(Event.starts_at)
        .options(selectinload(Event.translations), selectinload(Event.venue))
    ).all()

    cards = [(e, pick(e.translations, lang)) for e in events]

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"cards": cards, "lang": lang},
    )