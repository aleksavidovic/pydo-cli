
# pydo - CLI Design

This document outlines the command-line interface for pydo.

---

## Core Philosophy

- **Local First**: By default, all commands operate on the local list if one is found in the current directory or any parent directory (by searching for a `.pydo` file/directory).
- **Global Fallback**: If no local list is found, commands fall back to operating on the global list.
- **Explicit Override**: A `--global` (`-g`) flag can be used with any command to force it to operate on the global list, ignoring any local context.

---

## List Management

These commands manage the todo lists themselves.

### `pydo init`

- **Action**: Initializes a new, empty local todo list in the current directory. It will create a hidden `.pydo` file or directory to act as the root marker for the local list.
- **Behavior**: If a local list already exists in this directory, it should do nothing and inform the user.
- **Example**:
  ```bash
  ~/projects/my-cool-app$ pydo init
  ✅ Local pydo list initialized in /home/user/projects/my-cool-app

### `pydo status`

* **Action**: Shows which list is currently active.
* **Examples**:

  ```bash
  # Inside a project with a local list
  ~/projects/my-cool-app$ pydo status
  - Active list: Local (/home/user/projects/my-cool-app)
  
  # In a directory without a local list
  ~/Downloads$ pydo status
  - Active list: Global
  ```

---

## Task Management

These are the primary commands for interacting with tasks. They all adhere to the local-first/global-override rule.

### `pydo` or `pydo list` (aliased as `ls`)

* **Action**: Displays the tasks on the active list.
* **Output**: Should show a unique ID, the task status (e.g., `[ ]` or `[x]`), and the task description.
* **Flags**:

  * `--all` (`-a`): Show all tasks, including completed ones.
  * `--done`: Show only completed tasks.
* **Examples**:

  ```bash
  # Show pending tasks on the active list
  $ pydo

  # Show all tasks on the active list
  $ pydo list --all

  # Explicitly show pending tasks from the global list
  $ pydo ls --global
  ```

### `pydo add <TASK_DESCRIPTION>`

* **Action**: Adds a new task to the active list. The task description should be enclosed in quotes if it contains spaces.
* **Examples**:

  ```bash
  $ pydo add "Set up the database schema"
  ✅ Added task: [1] Set up the database schema

  # Add a task to the global list from anywhere
  $ pydo add --global "Call the dentist"
  ```

### `pydo done <TASK_ID...>`

* **Action**: Marks one or more tasks as complete, identified by their IDs.
* **Example**:

  ```bash
  $ pydo done 1 3
  ✅ Completed task: [1] Set up the database schema
  ✅ Completed task: [3] Write API documentation
  ```

### `pydo undone <TASK_ID...>`

* **Action**: Reverts one or more completed tasks to pending.
* **Example**:

  ```bash
  $ pydo undone 1
  ✅ Marked task as pending: [1] Set up the database schema
  ```

### `pydo edit <TASK_ID> <NEW_DESCRIPTION>`

* **Action**: Modifies the description of an existing task.
* **Example**:

  ```bash
  $ pydo edit 1 "Set up the PostgreSQL database schema"
  ```

### `pydo remove <TASK_ID...>` (aliased as `rm`)

* **Action**: Permanently removes one or more tasks from the list.
* **Flags**:

  * `--force` (`-f`): Skips any confirmation prompt.
* **Example**:

  ```bash
  $ pydo rm 3
  Are you sure you want to remove task 3? [y/N]: y
  ✅ Task 3 removed.
  ```

### `pydo clear`

* **Action**: Permanently removes all completed tasks from the active list. Useful for cleaning up.
* **Flags**:

  * `--force` (`-f`): Skips any confirmation prompt.
* **Example**:

  ```bash
  $ pydo clear
  ```



