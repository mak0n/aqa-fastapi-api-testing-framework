from pydantic import BaseModel


class UserPublic(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool | None = True
    is_superuser: bool | None = False

class Token(BaseModel):
    access_token: str
    token_type: str

class ItemPublic(BaseModel):
    id: str
    title: str
    description: str | None = None
    owner_id: str
