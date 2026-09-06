from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from db import get_session
from deps import common, pick
from filters import templates
from models import Book, Genre, Loan

router = APIRouter()


@router.get("/{lang}/library/")
def library(request: Request, ctx: dict = Depends(common),
            session: Session = Depends(get_session)):
    lang = ctx["lang"]

    books = session.scalars(
        select(Book)
        .options(
            selectinload(Book.translations),
            selectinload(Book.genres).selectinload(Genre.translations),
        )
        .order_by(Book.author_latin, Book.title_original)
    ).all()

    on_loan = set(session.scalars(
        select(Loan.book_id).where(Loan.returned_at.is_(None))
    ).all())

    return templates.TemplateResponse(
        request=request, name="library.html",
        context={
            **ctx,
            "books": [(b, pick(b.translations, lang)) for b in books],
            "on_loan": on_loan,
        },
    )