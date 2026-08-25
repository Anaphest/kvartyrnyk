from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from i18n import translator

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
def switch_lang(request: Request, target: str) -> str:
    """Той самий шлях, інша мова: /uk/event/x → /en/event/x"""
    parts = request.url.path.split("/")
    if len(parts) > 1 and parts[1] in LANGS:
        parts[1] = target
        return "/".join(parts)
    return f"/{target}/"


templates.env.globals["switch_lang"] = switch_lang
templates.env.globals["LANGS"] = LANGS

def common(lang: str) -> dict:
    if lang not in LANGS:
        raise HTTPException(status_code=404)
    return {"lang": lang, "_": translator(lang)}


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
def home(request: Request, ctx: dict = Depends(common),
         session: Session = Depends(get_session)):
    lang = ctx["lang"]
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
            **ctx,
            "upcoming": [(e, t) for e in upcoming if (t := pick(e.translations, lang))],
            "past": [(e, t) for e in past if (t := pick(e.translations, lang))],
        },
    
    )


@app.get("/{lang}/about")
def about(request: Request, ctx: dict = Depends(common)):
    return templates.TemplateResponse(
        request=request, name="about.html", context=ctx,
    )


@app.get("/{lang}/event/{slug}")
def event_page(slug: str, request: Request, ctx: dict = Depends(common),
               session: Session = Depends(get_session)):

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

    t = pick(event.translations, ctx["lang"])
    if t is None:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        request=request, name="event.html",
        context={**ctx, "event": event, "t": t},
    )

from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        lang = request.path_params.get("lang", "uk")
        if lang not in LANGS:
            lang = "uk"
        return templates.TemplateResponse(
            request=request, name="404.html",
            context={"lang": lang, "_": translator(lang)}, status_code=404,
        )
    return HTMLResponse(f"<h1>{exc.status_code}</h1>", status_code=exc.status_code)