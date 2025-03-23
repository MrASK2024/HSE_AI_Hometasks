from datetime import datetime
from pydantic import BaseModel


class ShortenLinksCreate(BaseModel):
    url: str
    short_link: str
    creation_date: datetime
    last_use_date: datetime
    expires_at: datetime
    user_id: str