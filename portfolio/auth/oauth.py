from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError, InvalidTokenError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Request
from typing import Optional
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from models import user
from decouple import config
from database import database



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def hash_password(password):
        return pwd_context.hash(password)


def create_access_token(user):
    try:
        payload = {"id": user.id, "exp": datetime.utcnow() + timedelta(minutes=120)}
        return jwt.encode(payload, key=config('JWT_SECRET_KEY'), algorithm="HS256")
    except Exception as e:
        raise HTTPException(status_code=401, detail="something is wrong with the payload.")


class CustomHTTPBearer(HTTPBearer):
    async def __call__(
            self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:

        res = await super().__call__(request)
        try:
            payload = jwt.decode(res.credentials, config('JWT_SECRET_KEY'), algorithms=["HS256"])
            result = await database.fetch_one(user.select().where(user.c.id == payload["id"]))
            request.state.user = result
            return payload
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token is expired")
        except InvalidSignatureError:
            raise HTTPException(status_code=401, detail="Invalid signature")
        except InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")


