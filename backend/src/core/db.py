from collections.abc import Generator

from sqlmodel import Session, create_engine, select

from src.core.config import settings
from src.users.models import User
from src.users.schemas import (
    UserCreate,
)

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # from src.core.engine import engine
    # This works because the models are already imported and registered from src.models
    # SQLModel.metadata.create_all(engine)

    from src.users.services import create_user  # Local import to avoid circular dependency

    user = session.exec(select(User).where(User.email == settings.FIRST_SUPERUSER)).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )

        user = create_user(session=session, user_create=user_in)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
