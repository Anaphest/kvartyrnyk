from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from filters import templates, LANGS
from i18n import translator
from routers import events, pages

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages.router)
app.include_router(events.router)


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