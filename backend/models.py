from pydantic import BaseModel, field_validator
from pathlib import Path


class TextResponse(BaseModel):
    text: str

    @field_validator("text")
    def check_response(cls, x):
        if x == "":
            return 0
        else:
            return x


class TextRequest(BaseModel):
    text: str

    @field_validator("text")
    def check_request(cls, x):
        if x == "":
            return 0
        else:
            return x


class PathResponse(BaseModel):
    path: Path

    @field_validator("path")
    def check_response(cls, x):
        if x == "":
            return 0
        else:
            return x


class PathRequest(BaseModel):
    path: Path

    @field_validator("path")
    def check_request(cls, x):
        if x == "":
            return 0
        else:
            return x


class QueryRequest(BaseModel):
    text: str
    collection_name: str
    k: int

    @field_validator("text", "collection_name")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty")
        return v

    @field_validator("k")
    @classmethod
    def positive_k(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("k must be > 0")
        return v


class PdfsRequest(BaseModel):
    paths: list[Path]

    @field_validator("paths")
    def check_request(cls, x):
        if x == "":
            return 0
        else:
            return x
