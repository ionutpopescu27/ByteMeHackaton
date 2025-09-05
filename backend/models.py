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
