from pathlib import Path
import uuid
from pydo.models import PydoData, Task


class PydoList:
    def __init__(self, path: Path):
        self._path = path
        self._data = self._load()

    def _load(self) -> PydoData:
        if not self._path.exists():
            return PydoData()
        with self._path.open("r") as f:
            return PydoData.model_validate(f.read())

    def _save(self):
        with self._path.open("w") as f:
            f.write(self._data.model_dump_json())

    def get_tasks(self, show_completed=True) -> list[Task]:
        return self._data.tasks

    def add_task(self, description: str) -> Task:
        new_task = Task(id=uuid.UUID(), description=description)
        self._data.tasks.append(new_task)
        self._save()
        return new_task

    def complete_tasks(self, task_ids: list[int]) -> int:
        if len(self._data.tasks) == 0:
            return 0
        completed_count = 0

        for task_id in sorted(list(set(task_ids))):
            if 1 <= task_id <= len(self._data.tasks):
                task = self._data.tasks[task_id-1]
                if not task.completed:
                    task.completed = True
                    completed_count += 1

        if completed_count > 0:
            self._data.metadata.total_completed_tasks += completed_count
            self._save()

        return completed_count
