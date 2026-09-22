# from datetime import datetime

# from sqlmodel import Field, SQLModel


# class SearchLog(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     endpoint: str          # e.g. "weather", "crypto", "github"
#     query: str             # e.g. "London", "bitcoin", "torvalds"
#     result_summary: str    # short text summary of what came back
#     created_at: datetime = Field(default_factory=datetime.utcnow)

from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SearchLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    endpoint: str
    query: str
    result_summary: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))