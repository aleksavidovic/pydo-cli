import argparse
import sys
from pathlib import Path

class Backend:
    def __init__(self, is_global, path=None):
        self.is_global = is_global
        self.list_path = path
        print(f"DEBUG: Backend initialized for {'global' if is_global else 'local'} list at {path}")

    def init_list(self):
        print("BACKEND: Initializing new list...")
    
    def add_task(self, description):
        print(f"BACKEND: Adding task '{description}'")

    def list_tasks(self, show_all=False, show_done=False):
        print(f"BACKEND: Listing tasks (all={show_all}, done={show_done})")
        print("  [1] [ ] Task one from backend")
        print("  [2] [x] Task two from backend")

    def complete_tasks(self, task_ids):
        print(f"BACKEND: Completing tasks {task_ids}")

    def uncomplete_tasks(self, task_ids):
        print(f"BACKEND: Un-completing tasks {task_ids}")

    def edit_task(self, task_id, new_description):
        print(f"BACKEND: Editing task {task_id} to '{new_description}'")

    def remove_tasks(self, task_ids, force=False):
        print(f"BACKEND: Removing tasks {task_ids} (force={force})")

    def clear_completed(self, force=False):
        print(f"BACKEND: Clearing completed tasks (force={force})")

# --- Context Resolution ---

def find_local_list_path():
    """
    Traverse up from the current directory to find a '.pydo' file/directory.
    Returns the Path object if found, otherwise None.
    """
    current_dir = Path.cwd()
    while current_dir != current_dir.parent:
        if (current_dir / ".pydo").exists():
            return (current_dir / ".pydo")
        current_dir = current_dir.parent
    return None

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


# --- CLI Command Handlers ---

def handle_init(args):
    # This command ONLY works locally.
    if (Path.cwd() / ".pydo").exists():
        print(f"Local pydo list already exists in {Path.cwd()}")
        return
    
    backend = Backend(is_global=False, path=Path.cwd() / ".pydo")
    backend.init_list()
    print(f"✅ Local pydo list initialized in {Path.cwd()}")

def handle_status(args):
    # This command also ignores the --global flag
    local_path = find_local_list_path()
    if local_path:
        print(f"- Active list: Local ({local_path.parent})")
    else:
        print("- Active list: Global")

def handle_list(args):
    backend = args.backend
    backend.list_tasks(show_all=args.all, show_done=args.done)

def handle_add(args):
    backend = args.backend
    description = " ".join(args.description)
    backend.add_task(description)

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
    if 'func' in args and args.command not in ['init', 'status']:
        if args.glob:
             # User explicitly asked for global
            global_path = Path.home() / ".pydo_global"
            args.backend = Backend(is_global=True, path=global_path)
        else:
            # Default behavior: local-first
            args.backend = get_backend()
    
    args.func(args)


if __name__ == "__main__":
    # Allows running the script directly for testing,
    # e.g., python src/my_cli_tool/main.py add "Test task"
    # Note: `sys.argv` will be like ['src/my_cli_tool/main.py', 'add', 'Test task']
    run()
