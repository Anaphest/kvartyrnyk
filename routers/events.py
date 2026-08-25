from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from db import get_session
from deps import common, pick
from filters import templates
from models import Event

router = APIRouter()


@router.get("/{lang}/")
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


@router.get("/{lang}/event/{slug}")
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