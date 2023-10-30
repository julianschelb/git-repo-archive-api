from pydantic import BaseModel


class APIKey(BaseModel):
    key: str
