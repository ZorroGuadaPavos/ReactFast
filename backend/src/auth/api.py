from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.schemas import NewPassword, Token
from src.auth.services import SessionDep, get_password_hash, verify_password_reset_token
from src.core.config import settings
from src.core.schemas import Message
from src.users.services import get_user_by_email

from . import services

router = APIRouter()


@router.post('/login/access-token')
def login_access_token(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = services.authenticate(session=session, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail='Incorrect email or password')
    elif not user.is_active:
        raise HTTPException(status_code=400, detail='Inactive user')
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(access_token=services.create_access_token(user.id, expires_delta=access_token_expires))


@router.post('/reset-password/')
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password
    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail='Invalid token')
    user = get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail='The user with this email does not exist in the system.',
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail='Inactive user')
    hashed_password = get_password_hash(password=body.new_password)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    return Message(message='Password updated successfully')
