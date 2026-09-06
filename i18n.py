STRINGS = {
    # загальне
    "site_title": {
        "uk": "Квартирник",
        "en": "Kvartyrnyk",
        "sv": "Kvartyrnyk",
    },

    # меню
    "nav_events": {
        "uk": "Події",
        "en": "Events",
        "sv": "Evenemang",
    },
    "nav_library": {
        "uk": "Бібліотека",
        "en": "Library",
        "sv": "Bibliotek",
    },
    "nav_about": {
        "uk": "Про нас",
        "en": "About",
        "sv": "Om oss",
    },
    "nav_poetry": {
        "uk": "Переклади",
        "en": "Translations",
        "sv": "Översättningar",
    },

    # головна
    "no_upcoming": {
        "uk": "Найближчих подій поки немає.",
        "en": "No upcoming events yet.",
        "sv": "Inga kommande evenemang än.",
    },
    "past_events": {
        "uk": "Минулі події",
        "en": "Past events",
        "sv": "Tidigare evenemang",
    },

    # про нас
    "about_text": {
        "uk": "Ми поєднуємо культури України і Скандинавії, щоб створювати спільний сенс й підтримувати Збройні Сили",
        "en": "We connect cultures of Ukraine and Nordics to build shared meaning and support the Defence Forces",
        "sv": "Vi kopplar samman kulturer från Ukraina och Norden för att bygga gemensam betydelse och stödja Försvarsmakten",
    },

    "not_found": {
        "uk": "Такої сторінки немає.",
        "en": "This page does not exist.",
        "sv": "Sidan finns inte.",
    },
    
    "back_home": {
        "uk": "На головну",
        "en": "Back to home",
        "sv": "Till startsidan",
    },

    # бібліотека
    "library": {
        "uk": "Бібліотека",
        "en": "Library",
        "sv": "Bibliotek",
    },
    "library_empty": {
        "uk": "Бібліотека порожня",
        "en": "The library is empty",
        "sv": "Biblioteket är tomt",
    },
    "book_on_loan": {
        "uk": "зараз читають",
        "en": "currently borrowed",
        "sv": "utlånad just nu",
    },

    
}


def translator(lang: str):
    def _(key: str) -> str:
        return STRINGS.get(key, {}).get(lang, key)
    return _