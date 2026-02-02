from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timezone
from typing import Optional

class User(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    password: str
    name: Optional[str] = None
    nivel: str = "common"
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    is_active: bool = True