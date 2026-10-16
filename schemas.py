from pydantic import BaseModel


class UserPublic(BaseModel):
    id: str
    email: str
    full_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False


class Token(BaseModel):
    access_token: str
    token_type: str


class ItemPublic(BaseModel):
    id: str
    title: str
    description: str | None = None
    owner_id: str
