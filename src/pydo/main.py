import pdb
import uuid
import json
import argparse
import sys
from pathlib import Path

# --- Context Resolution ---

def find_local_list_path():
    """
    Traverse up from the current directory to find a '.pydo' file/directory.
    Returns the Path object if found, otherwise None.
    """
    current_dir = Path.cwd()
    while current_dir != current_dir.parent:
        if (current_dir / ".pydo" / "tasks.json").exists():
            return (current_dir / ".pydo" / "tasks.json")
        current_dir = current_dir.parent
    return None

def get_global_list_path():
    return Path.home() / ".pydo" / "tasks.json"

def get_backend():
    """
    Determines whether to use the global or local backend.
    This is a placeholder for your actual context resolution.
    """
    # This check will be overridden by the --global flag later
    local_path = find_local_list_path()
    if local_path:
        return Backend(is_global=False, path=local_path)
    
    # You need to define where your global list is stored
    global_path = Path.home() / ".pydo_global"
    return Backend(is_global=True, path=global_path)
"""
{
  "schema_version": 1,
  "tasks": [
    {
      "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
      "description": "Set up the database schema",
      "completed": false
    },
    {
      "id": "f9e8d7c6-b5a4-4f3e-2d1c-0b9a8f7e6d5c",
      "description": "Write API documentation",
      "completed": false
    }
  ]
}
"""
# --- Helper Functions (Save / Load) ---
def save_tasks(path: Path, data: dict):
    with path.open('w') as f:
        json.dump(data, f, indent=2)

def load_tasks(path: Path):
    if not path.exists():
        return {"schema_version": 1, "tasks": []}
    with path.open('r') as f:
        return json.load(f)

def print_tasks(tasks, show_all=False, show_done=True):
    print(f"Listing tasks (all={show_all}, done={show_done})")
    print("ID  Status  Description")
    print("--  ------  -----------")
    for display_id, task in enumerate(tasks, 1):
        status = "[x]" if task['completed'] else "[ ]"
        print(f"{display_id:<3} {status:<7} {task['description']}")

# --- CLI Command Handlers ---

def handle_init(args):
    current_dir = Path.cwd()
    pydo_dir = current_dir / ".pydo"
    tasks_file = pydo_dir / "tasks.json"

    if tasks_file.is_file():
        print(f"pydo already initialized in {current_dir}")
        return

    print(f"Creating pydo directory at {pydo_dir}...")
    pydo_dir.mkdir(exist_ok=True)

    initial_data = {
        "schema_version": 1,
        "tasks": []
    }
    
    print(f"Creating tasks file at {tasks_file}...")
    tasks_file.write_text(json.dumps(initial_data, indent=2))
    
    print(f"🎉 Successfully initialized pydo list in {current_dir}")
                

def handle_status(args):
    # This command also ignores the --global flag
    local_path = find_local_list_path()
    if local_path == Path.home() / ".pydo":
        print("- Active list: Global")
        return
    if local_path and (local_path != Path.home()):
        print(f"- Active list: Local ({local_path.parent})")
    else:
        print("- Active list: Global")

def handle_list(args):
    path = find_local_list_path()
    if path is not None:
        data = load_tasks(path)
        print_tasks(data["tasks"], show_all=args.all, show_done=args.done)
    else:
        print(f"Task loading failed. Are you sure pydo is initialized here ({path})?")

def handle_add(args):
    path = find_local_list_path()
    if path == None:
        path = get_global_list_path()
    try:
        with open(path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Task creation failed. Are you sure pydo is initialized here ({path})?")
        return
    description = " ".join(args.description)
    new_task = {
            "id": str(uuid.uuid4()),
            "description": description,
            "completed": False
    }
    data["tasks"].append(new_task)
    save_tasks(path, data)

def handle_done(args):
    backend = args.backend
    backend.complete_tasks(args.task_ids)

def handle_undone(args):
    backend = args.backend
    backend.uncomplete_tasks(args.task_ids)

def handle_edit(args):
    backend = args.backend
    new_description = " ".join(args.new_description)
    backend.edit_task(args.task_id, new_description)

def handle_remove(args):
    backend = args.backend
    backend.remove_tasks(args.task_ids, force=args.force)

def handle_clear(args):
    backend = args.backend
    backend.clear_completed(force=args.force)


# --- Main Entry Point & Argument Parsing ---

def run():
    parser = argparse.ArgumentParser(
        prog="pydo",
        description="A simple command-line todo list manager."
    )
    # This is a top-level flag that affects context for most sub-commands.
    parser.add_argument(
        '-g', '--global',
        action='store_true',
        help='Force operation on the global todo list.'
    )

    subparsers = parser.add_subparsers(dest='command', required=True, help='Sub-command help')

    # Command: init
    parser_init = subparsers.add_parser('init', help='Initialize a local todo list in the current directory.')
    parser_init.set_defaults(func=handle_init)

    # Command: status
    parser_status = subparsers.add_parser('status', help='Show the currently active list (local or global).')
    parser_status.set_defaults(func=handle_status)

    # Command: list / ls
    parser_list = subparsers.add_parser('list', help='List tasks.', aliases=['ls'])
    parser_list.add_argument('-a', '--all', action='store_true', help='Show all tasks, including completed ones.')
    parser_list.add_argument('--done', action='store_true', help='Show only completed tasks.')
    parser_list.set_defaults(func=handle_list)

    # Command: add
    parser_add = subparsers.add_parser('add', help='Add a new task.')
    parser_add.add_argument('description', nargs='+', help='The description of the task.')
    parser_add.set_defaults(func=handle_add)
    
    # Command: done
    parser_done = subparsers.add_parser('done', help='Mark task(s) as done.')
    parser_done.add_argument('task_ids', nargs='+', type=int, help='The ID(s) of the task(s) to mark as done.')
    parser_done.set_defaults(func=handle_done)

    # Command: undone
    parser_undone = subparsers.add_parser('undone', help='Mark task(s) as not done.')
    parser_undone.add_argument('task_ids', nargs='+', type=int, help='The ID(s) of the task(s) to mark as not done.')
    parser_undone.set_defaults(func=handle_undone)

    # Command: edit
    parser_edit = subparsers.add_parser('edit', help='Edit a task.')
    parser_edit.add_argument('task_id', type=int, help='The ID of the task to edit.')
    parser_edit.add_argument('new_description', nargs='+', help='The new description for the task.')
    parser_edit.set_defaults(func=handle_edit)

    # Command: remove / rm
    parser_remove = subparsers.add_parser('remove', help='Remove task(s).', aliases=['rm'])
    parser_remove.add_argument('task_ids', nargs='+', type=int, help='The ID(s) of the task(s) to remove.')
    parser_remove.add_argument('-f', '--force', action='store_true', help='Remove without confirmation.')
    parser_remove.set_defaults(func=handle_remove)
    
    # Command: clear
    parser_clear = subparsers.add_parser('clear', help='Remove all completed tasks.')
    parser_clear.add_argument('-f', '--force', action='store_true', help='Clear without confirmation.')
    parser_clear.set_defaults(func=handle_clear)

    # --- Execution ---
    args = parser.parse_args(sys.argv[1:])
    # Centrally decide which backend to use based on the --global flag
    # and attach it to the args object for handlers to use.
    """
    if 'func' in args and args.command not in ['init', 'status']:
        if args.global:
             # User explicitly asked for global
            global_path = Path.home() / ".pydo_global"
            args.backend = Backend(is_global=True, path=global_path)
        else:
            # Default behavior: local-first
            args.backend = get_backend()
    """
    
    args.func(args)


if __name__ == "__main__":
    # Allows running the script directly for testing,
    # e.g., python src/my_cli_tool/main.py add "Test task"
    # Note: `sys.argv` will be like ['src/my_cli_tool/main.py', 'add', 'Test task']
    run()
