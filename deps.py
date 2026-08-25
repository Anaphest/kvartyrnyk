from fastapi import HTTPException

from filters import LANGS
from i18n import translator

FALLBACK = {"uk": ["uk", "en"], "en": ["en", "uk"], "sv": ["sv", "en", "uk"]}


def pick(translations, lang):
    by_lang = {t.lang: t for t in translations}
    for candidate in FALLBACK[lang]:
        if candidate in by_lang:
            return by_lang[candidate]
    # останній рубіж: будь-який наявний переклад краще, ніж 500
    return next(iter(by_lang.values()), None)


def common(lang: str) -> dict:
    if lang not in LANGS:
        raise HTTPException(status_code=404)
    return {"lang": lang, "_": translator(lang)}