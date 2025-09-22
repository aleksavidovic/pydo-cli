import json
import uuid
from pathlib import Path

from pydo.models import CURRENT_SCHEMA_VERSION, Metadata, PydoData, Task


class PydoList:
    def __init__(self, path: Path):
        self._path = path
        self._data = self._load()

    def _load(self) -> PydoData:
        if not self._path.exists():
            return PydoData()
        with self._path.open("r") as f:
            raw_data = json.load(f)
        schema_version = raw_data.get("schema_version", 1)
        if schema_version < CURRENT_SCHEMA_VERSION:
            raw_data = self._migrate(raw_data, from_version=schema_version)
        pydo_data = PydoData.model_validate(raw_data)
        self._save_data(pydo_data)

        return pydo_data

    def _migrate(self, data: dict, from_version=1) -> dict:
        if from_version == 1:
            data["schema_version"] = 2
        return data

    def _save_data(self, data: PydoData):
        with self._path.open("w") as f:
            f.write(data.model_dump_json())

    def _save(self):
        with self._path.open("w") as f:
            f.write(self._data.model_dump_json())

    def get_tasks(self, show_completed=True) -> list[Task]:
        return self._data.tasks

    def get_metadata(self) -> Metadata:
        return self._data.metadata

    def get_list_name(self) -> str:
        return self._data.metadata.local_list_name

    def get_list_google_id(self) -> str:
        return self._data.metadata.google_tasks_list_id

    def set_list_google_id(self, google_id: str):
        self._data.metadata.google_tasks_list_id = google_id
        self._save()

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
                task = self._data.tasks[task_id - 1]
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
                task = self._data.tasks[task_id - 1]
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

    def hide_tasks(self, task_ids: list[int]) -> tuple[int, int]:
        hidden_count = 0
        skipped_count = 0
        for task_id in sorted(list(set(task_ids))):
            if 1 <= task_id <= len(self._data.tasks):
                if not self._data.tasks[task_id - 1].hidden:
                    self._data.tasks[task_id - 1].hidden = True
                    hidden_count += 1
                else:
                    skipped_count += 1
        if hidden_count > 0:
            self._save()
        return hidden_count, skipped_count

    def unhide_tasks(self, task_ids: list[int]) -> tuple[int, int]:
        unhidden_count = 0
        skipped_count = 0
        for task_id in sorted(list(set(task_ids))):
            if 1 <= task_id <= len(self._data.tasks):
                if self._data.tasks[task_id - 1].hidden:
                    self._data.tasks[task_id - 1].hidden = False
                    unhidden_count += 1
                else:
                    skipped_count += 1
        if unhidden_count > 0:
            self._save()
        return unhidden_count, skipped_count

    def remove_tasks(self, task_ids: list[int]) -> tuple[int, int]:
        if len(self._data.tasks) == 0:
            return 0, 0
        removed_count = 0
        skipped_count = 0
        old_task_count = len(self._data.tasks)
        ids_to_remove = [
            task_id - 1
            for task_id in sorted(list(set(task_ids)))
            if 1 <= task_id <= len(self._data.tasks)
        ]
        new_tasks = [
            task for i, task in enumerate(self._data.tasks) if i not in ids_to_remove
        ]
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
