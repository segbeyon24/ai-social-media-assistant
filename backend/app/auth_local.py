"""
Local authentication module (Option A) for AI Social Manager.
- Provides /auth/register and /auth/login endpoints
- Uses bcrypt for password hashing
- Issues JWTs signed with JWT_SECRET (env)
- Provides dependency `get_current_user` to protect routes

Security notes:
- JWT_SECRET must be a strong secret stored in env.
- Tokens are short-lived (configurable). Use refresh tokens for long sessions if desired.
"""
import os
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr
import bcrypt
import jwt
from datetime import datetime, timedelta
from .db import db

router = APIRouter(prefix='/auth')

JWT_SECRET = 'dev-ai-social-media-assistantv_01' #os.getenv('JWT_SECRET')
if not JWT_SECRET:
    raise RuntimeError('JWT_SECRET env var must be set')
JWT_ALGORITHM = 'HS256'
JWT_EXP_MINUTES = int(os.getenv('JWT_EXP_MINUTES', '1440'))  # default 24 hours


class RegisterIn(BaseModel):
    email: EmailStr
    password: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_jwt(user_id: str):
    expire_minutes = int(JWT_EXP_MINUTES)
    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)

    payload = {
        "sub": str(user_id),
        "user_id": str(user_id),
        "exp": expire
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token



def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except Exception as e:
        raise HTTPException(status_code=401, detail=f'Invalid token: {e}')


async def get_current_user(authorization: str = Depends(lambda: None)):
    # This is a wrapper used by FastAPI dependency injection in main.py via Depends(get_current_user)
    # But actual wiring is done by providing a dependency that reads the Authorization header.
    raise RuntimeError('get_current_user should be overridden with header dependency in main')


@router.post('/register')
async def register(payload: RegisterIn):
    # Check if user exists
    q = 'SELECT id, email FROM users WHERE email = :email'
    existing = await db.fetch_one(q, values={'email': payload.email})
    if existing:
        raise HTTPException(status_code=400, detail='Email already registered')
    hashed = hash_password(payload.password)
    q = 'INSERT INTO users (email, password_hash) VALUES (:email, :ph) RETURNING id'
    row = await db.fetch_one(q, values={'email': payload.email, 'ph': hashed})
    user_id = row['id']
    token = create_jwt(user_id)
    return {'access_token': token, 'token_type': 'bearer', 'user_id': user_id}


@router.post('/login')
async def login(payload: LoginIn):
    q = 'SELECT id, email, password_hash FROM users WHERE email = :email'
    row = await db.fetch_one(q, values={'email': payload.email})
    if not row:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    if not verify_password(payload.password, row['password_hash']):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    token = create_jwt(row['id'])
    return {'access_token': token, 'token_type': 'bearer', 'user_id': row['id']}
