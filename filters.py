from datetime import timezone
from zoneinfo import ZoneInfo

from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

TZ = ZoneInfo("Europe/Stockholm")

LANGS = ("uk", "en", "sv")

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


def switch_lang(request: Request, target: str) -> str:
    """Той самий шлях, інша мова: /uk/event/x → /en/event/x"""
    parts = request.url.path.split("/")
    if len(parts) > 1 and parts[1] in LANGS:
        parts[1] = target
        return "/".join(parts)
    return f"/{target}/"


templates.env.filters["dt"] = dt
templates.env.filters["month_year"] = month_year
templates.env.globals["switch_lang"] = switch_lang
templates.env.globals["LANGS"] = LANGS