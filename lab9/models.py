"""Схемы входа/выхода API (валидация на HTTP-границе)."""
from typing import Optional

from pydantic import BaseModel, Field, model_validator

ISBN_PATTERN = r"^[0-9]{3}-[0-9]-[0-9]{2,5}-[0-9]{2,7}-[0-9]$"  # напр. 978-5-17-123456-7


class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    year: int = Field(ge=1450, le=2100)
    copies: int = Field(default=1, ge=0, le=10_000, description="Экземпляров в фонде")


class BookCreate(BookBase):
    isbn: str = Field(pattern=ISBN_PATTERN)


class BookUpdate(BaseModel):
    """PATCH: все поля необязательны, isbn изменить нельзя."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    author: Optional[str] = Field(default=None, min_length=1, max_length=100)
    category: Optional[str] = Field(default=None, min_length=1, max_length=50)
    year: Optional[int] = Field(default=None, ge=1450, le=2100)
    copies: Optional[int] = Field(default=None, ge=0, le=10_000)

    @model_validator(mode="after")
    def at_least_one_field(self):
        if not self.model_fields_set:
            raise ValueError("Нужно передать хотя бы одно поле для изменения")
        return self


class Book(BookBase):
    isbn: str
