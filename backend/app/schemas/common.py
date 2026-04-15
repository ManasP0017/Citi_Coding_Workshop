"""Shared response schemas."""

from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class CreatedResponse(BaseModel):
    message: str
    id: str
