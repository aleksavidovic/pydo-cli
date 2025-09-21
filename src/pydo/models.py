from uuid import UUID
from pydantic import BaseModel


class Metadata(BaseModel):
    local_list_name: str = ""
    google_tasks_list_id: str = ""
    total_completed_tasks: int = 0

class Task(BaseModel):
    id: UUID
    description: str
    completed: bool = False
    focus: bool | None = None

class PydoData(BaseModel):
    schema_version: int = 1
    metadata: Metadata = Metadata()
    tasks: list[Task] = []

