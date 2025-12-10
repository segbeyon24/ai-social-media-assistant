from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StoreAIKeyIn(BaseModel):
    provider: str
    api_key: str


class GenerateIn(BaseModel):
    provider: str
    prompt: str
    model: Optional[str] = 'gpt-4o'


class ScheduleIn(BaseModel):
    user_id: str
    social_account_id: str
    content: str
    scheduled_at: datetime