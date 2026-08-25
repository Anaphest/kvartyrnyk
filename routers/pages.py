from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from deps import common
from filters import templates

router = APIRouter()


@router.get("/")
def root():
    return RedirectResponse("/uk/")


@router.get("/{lang}/about")
def about(request: Request, ctx: dict = Depends(common)):
    return templates.TemplateResponse(
        request=request, name="about.html", context=ctx,
    )