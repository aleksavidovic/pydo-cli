from uuid import UUID

from pydantic import BaseModel

CURRENT_SCHEMA_VERSION = 2


class Metadata(BaseModel):
    local_list_name: str = ""
    google_tasks_list_id: str = ""
    total_completed_tasks: int = 0


class Task(BaseModel):
    id: UUID
    description: str
    completed: bool = False
    focus: bool | None = False
    hidden: bool = False


class PydoData(BaseModel):
    schema_version: int = CURRENT_SCHEMA_VERSION
    metadata: Metadata = Metadata()
    tasks: list[Task] = []
