from pathlib import Path
import uuid
import json
from pydo.models import PydoData, Task, Metadata


class PydoList:
    def __init__(self, path: Path):
        self._path = path
        self._data = self._load()

    def _load(self) -> PydoData:
        if not self._path.exists():
            return PydoData()
        with self._path.open("r") as f:
            return PydoData.model_validate(json.load(f))

    def _save(self):
        with self._path.open("w") as f:
            f.write(self._data.model_dump_json())

    def get_tasks(self, show_completed=True) -> list[Task]:
        return self._data.tasks

    def get_metadata(self) -> Metadata:
        return self._data.metadata

    def get_list_name(self) -> str:
        return self._data.metadata.local_list_name

    def add_task(self, description: str) -> Task:
        new_task = Task(id=uuid.uuid4(), description=description)
        self._data.tasks.append(new_task)
        self._save()
        return new_task

    def complete_tasks(self, task_ids: list[int]) -> tuple[int, int]:
        if len(self._data.tasks) == 0:
            return 0, 0
        completed_count = 0
        skipped_count = 0
        for task_id in sorted(list(set(task_ids))):
            if 1 <= task_id <= len(self._data.tasks):
                task = self._data.tasks[task_id-1]
                if not task.completed:
                    task.completed = True
                    completed_count += 1
                else:
                    skipped_count += 1
            else:
                skipped_count += 1

        if completed_count > 0:
            self._data.metadata.total_completed_tasks += completed_count
            self._save()

        return completed_count, skipped_count

    def uncomplete_tasks(self, task_ids: list[int]) -> tuple[int, int]:
        if len(self._data.tasks) == 0:
            return 0, 0
        uncompleted_count = 0
        skipped_count = 0
        for task_id in sorted(list(set(task_ids))):
            if 1 <= task_id <= len(self._data.tasks):
                task = self._data.tasks[task_id-1]
                if task.completed:
                    task.completed = False
                    uncompleted_count += 1
                else:
                    skipped_count += 1
            else:
                skipped_count += 1

        if uncompleted_count > 0:
            self._data.metadata.total_completed_tasks -= uncompleted_count
            self._save()

        return uncompleted_count, skipped_count

    def remove_tasks(self, task_ids: list[int]) -> tuple[int, int]:
        if len(self._data.tasks) == 0:
            return 0, 0
        removed_count = 0
        skipped_count = 0
        old_task_count = len(self._data.tasks)
        ids_to_remove = [task_id-1 for task_id in sorted(list(set(task_ids))) if 1 <= task_id <= len(self._data.tasks)]
        new_tasks = [task for i, task in enumerate(self._data.tasks) if i not in ids_to_remove]
        removed_count = old_task_count - len(new_tasks)
        if removed_count > 0:
            self._data.tasks = new_tasks
            self._save()
        return removed_count, skipped_count

    def toggle_focus(self, task_ids: list[int]) -> tuple[int, int]:
        focus_on_count = 0
        focus_off_count = 0
        for task_id in sorted(list(set(task_ids))):  # Sort and de-duplicate IDs
            if 1 <= task_id <= len(self._data.tasks):
                task = self._data.tasks[task_id - 1]

                if task.focus:
                    task.focus = False
                    focus_off_count += 1
                else:
                    task.focus = True
                    focus_on_count += 1

        if focus_on_count > 0 or focus_off_count > 0:
            self._save()

        return focus_on_count, focus_off_count

    def clear_completed_tasks(self) -> int:
        if len(self._data.tasks) == 0:
            return 0
        cleared_count = 0
        old_task_count = len(self._data.tasks)
        self._data.tasks = [task for task in self._data.tasks if not task.completed]
        cleared_count = old_task_count - len(self._data.tasks)
        if cleared_count > 0:
            self._save()
        return cleared_count
