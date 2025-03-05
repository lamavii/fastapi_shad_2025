from pydantic import BaseModel


class TokenData(BaseModel):
    email: str
    password: str
