from pydantic import BaseModel, field_validator, EmailStr, Field, ConfigDict
from passlib.context import CryptContext
from pydantic_core import PydanticCustomError

from src.schemas.books import SellerBook


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

__all__ = ["IncomingSeller", "ReturnedAllSellers", "ReturnedSeller", "ReturnedSellersDetails", "SellerUpdate"]


class BaseSeller(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr


class IncomingSeller(BaseSeller):
    password: str

    @field_validator("first_name", "last_name")
    @staticmethod
    def validate_name_fields(value: str, field: str):
        if not value.isalpha():
            raise PydanticCustomError("Validation error", f"{field} must contain only letters")
        return value

    @field_validator("password")
    @staticmethod
    def validate_password(value: str):
        if len(value) < 8:
            raise PydanticCustomError("Validation error", "Password must be at least 8 characters long")
        return value


class ReturnedSeller(BaseSeller):
    id: int


class ReturnedSellersDetails(ReturnedSeller):
    books: list[SellerBook]

    model_config = ConfigDict(from_attributes=True)


class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]


class SellerUpdate(BaseModel):
    first_name: str = Field(None, min_length=2, max_length=50)
    last_name: str = Field(None, min_length=2, max_length=50)
    email: EmailStr = None

    @field_validator("first_name", "last_name")
    @staticmethod
    def validate_name_fields(value: str, field: str):
        if not value.isalpha():
            raise PydanticCustomError("Validation error", f"{field} must contain only letters")
        return value
