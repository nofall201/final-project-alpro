from sqlmodel import SQLModel, Field
from datetime import datetime

class Detection(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime
    person_count: int
    violation_count: int
    screenshot_path: str | None
