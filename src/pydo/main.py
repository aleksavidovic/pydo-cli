import pdb
import time
import argparse
import json
import sys
import uuid
from pathlib import Path

from rich.table import Table

from pydo import console
from pydo.art import run_init_animation
# Single task structure
#{"id": str(uuid.uuid4()), "description": description, "completed": False}
TASKS_JSON_TEMPLATE = {
    "schema_version": 1, 
    "metadata": {
        "total_completed_tasks": 0  # Since task field is called "completed", this one has to follow
    }, 
    "tasks": []
}


# --- Context Resolution ---
def find_local_list_path():
    """
    Traverse up from the current directory to find a '.pydo' file/directory.
    Returns the Path object if found, otherwise None.
    """
    current_dir = Path.cwd()
    while current_dir != current_dir.parent:
        if (current_dir / ".pydo" / "tasks.json").exists():
            return current_dir / ".pydo" / "tasks.json"
        current_dir = current_dir.parent
    return None

def get_global_list_path():
    return Path.home() / ".pydo" / "tasks.json"

# --- Helper Functions (Save / Load) ---
def save_tasks(path: Path, data: dict):
    with path.open("w") as f:
        json.dump(data, f, indent=2)

def load_tasks(path: Path):
    if not path.exists():
        return TASKS_JSON_TEMPLATE 
    with path.open("r") as f:
        return json.load(f)

def print_tasks(tasks, show_all=False, show_done=True):
    table = Table(title="pydo tasks")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Status", style="magenta")
    table.add_column("Description")

    for display_id, task in enumerate(tasks, 1):
        status = "✅" if task["completed"] else "❌"
        description = task['description']
        style = "green strike dim" if task["completed"] else "yellow"
        table.add_row(str(display_id), status, description, style=style)

    console.print(table)


# --- CLI Command Handlers ---
def handle_init(args):
    current_dir = Path.cwd()
    pydo_dir = current_dir / ".pydo"
    tasks_file = pydo_dir / "tasks.json"

    if tasks_file.is_file():
        console.print(f"pydo already initialized in {current_dir}")
        return
    run_init_animation()

    console.print(f"Creating pydo directory at {pydo_dir}...")
    pydo_dir.mkdir(exist_ok=True)

    initial_data = TASKS_JSON_TEMPLATE

    console.print(f"Creating tasks file at {tasks_file}...")
    tasks_file.write_text(json.dumps(initial_data, indent=2))

    console.print(f"🎉 Successfully initialized pydo list in {current_dir}")


def handle_status(args): 
    local_path = find_local_list_path()
    if local_path == Path.home() / ".pydo":
        console.print("- Active list: Global")
        return
    if local_path and (local_path != Path.home()):
        console.print(f"- Active list: Local ({local_path.parent})")
        try:
            tasks = load_tasks(local_path)
            if "schema_version" not in tasks or (tasks["schema_version"] != 1):
                raise Exception("Issue with tasks.json: schema field incorrect")
            elif "metadata" not in tasks or "total_completed_tasks" not in tasks["metadata"]:
                raise Exception("Issue with tasks.json: metadata corrupted.")
        except Exception as e:
            console.print(f"[red bold]Error in data file: {e}")
    else:
        console.print("- Active list: Global")

def handle_list(args):
    path = find_local_list_path()
    if path is not None:
        data = load_tasks(path)
        print_tasks(data["tasks"], show_all=args.all, show_done=args.done)
        console.print(f'Total tasks done: {data["metadata"]["total_completed_tasks"]}')
    else:
        console.print(
            f"Task loading failed. Are you sure pydo is initialized here ({path})?"
        )



def handle_add(args):
    path = find_local_list_path()
    if path == None:
        path = get_global_list_path()
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        console.print(
            f"Task creation failed. Are you sure pydo is initialized here ({path})?"
        )
        return
    description = " ".join(args.description)
    new_task = {"id": str(uuid.uuid4()), "description": description, "completed": False}
    data["tasks"].append(new_task)
    save_tasks(path, data)
    console.print(f"✅ Added: '[yellow]{description}[/yellow]' to your [blue]local[/blue] list.")


def handle_done(args):
    path = find_local_list_path()
    if not path:
        console.print(
            "No local pydo list found. Use `pydo init` to create one in the current directory."
        )
        return
    data = load_tasks(path)
    if len(data["tasks"]) == 0:
        console.print("No tasks in the current list. Create one by using `pydo add`.")
        return

    tasks_completed_count = 0

    for task_id in sorted(list(set(args.task_ids))):  # Sort and de-duplicate IDs
        if (task_id - 1) < 0 or task_id > len(data["tasks"]):
            console.print(f"[bold red]Error:[/] Task ID {task_id} is invalid. Skipping.")
            continue
        
        task = data["tasks"][task_id - 1]

        if task["completed"]:
            console.print(f"Task {task_id}: '[yellow]{task['description']}[/yellow]' is already done.")
            continue

        with console.status(f"[bold green]Completing task {task_id}...", spinner="dots"):
            # This sleep makes the animation feel more deliberate
            time.sleep(0.7)
            task["completed"] = True
            tasks_completed_count += 1
        
        console.print(f"✅[strike dim green]{task['description']}[/strike dim green]")

    # 3. Save the data back to the file if changes were made
    if tasks_completed_count > 0:
        if not data["metadata"]:
            data["metadata"] = {"total_completed_tasks": tasks_completed_count}
        data["metadata"]["total_completed_tasks"] += tasks_completed_count
        save_tasks(path, data)
        if tasks_completed_count > 1:
             console.print(f"\n[bold green]Nice work! You've completed {tasks_completed_count} tasks. 🎉[/bold green]")
        else:
             console.print("[bold green]Nice work! 🎉[/bold green]")

def handle_undone(args):
    path = find_local_list_path()
    if not path:
        console.print(
            "No local pydo list found. Use `pydo init` to create one in the current directory."
        )
        return
    data = load_tasks(path)
    if len(data["tasks"]) == 0:
        console.print("No tasks in the current list. Create one by using `pydo add`.")
        return
    
    tasks_uncompleted_count = 0
    for task_id in sorted(list(set(args.task_ids))):  # Sort and de-duplicate IDs
        if (task_id - 1) < 0 or task_id > len(data["tasks"]):
            console.print(f"[bold red]Error:[/] Task ID {task_id} is invalid. Skipping.")
            continue
        
        task = data["tasks"][task_id - 1]

        if not task["completed"]:
            console.print(f"Task {task_id}: '[yellow]{task['description']}[/yellow]' is already not completed.")
            continue

        with console.status(f"[bold yellow]Reverting task status {task_id}...", spinner="dots"):
            # This sleep makes the animation feel more deliberate
            time.sleep(0.7)
            task["completed"] = False
            tasks_uncompleted_count += 1
        
        console.print(f"[strike dim yellow]{task['description']}[/strike dim yellow]")
        # 3. Save file and report progress

    if tasks_uncompleted_count > 0:
        data["metadata"]["total_completed_tasks"] -= tasks_uncompleted_count
        save_tasks(path, data)
        if tasks_uncompleted_count > 1:
             console.print(f"\n[bold yellow]You've changed {tasks_uncompleted_count} tasks back to not complete. Go get them! [/bold yellow]")
        else:
             console.print("[bold green]Task back in todo. Go get it![/bold green]")

def handle_edit(args):
    console.print("[bold red]Edit function not implemented yet.[/bold red]")

def handle_remove(args):
    path = find_local_list_path()
    if not path:
        console.print(
            "No local pydo list found. Use `pydo init` to create one in the current directory."
        )
        return
    data = load_tasks(path)
    if len(data["tasks"]) == 0:
        console.print("No tasks in the current list. Create one by using `pydo add`.")
        return
    
    tasks_deleted_count = 0
    for task_id in sorted(list(set(args.task_ids))):  # Sort and de-duplicate IDs
        if (task_id - 1) < 0 or task_id > len(data["tasks"]):
            console.print(f"[bold red]Error:[/] Task ID {task_id} is invalid. Skipping.")
            continue
        

        with console.status(f"[bold yellow]Removing task [strike dim green]{task_id}[/]...", spinner="dots"):
            # This sleep makes the animation feel more deliberate
            time.sleep(0.7)

            del(data["tasks"][task_id - 1])
            tasks_deleted_count += 1

    if tasks_deleted_count > 0:
        save_tasks(path, data)
        if tasks_deleted_count > 1:
             console.print(f"\n[bold yellow]You've deleted {tasks_deleted_count} tasks. [/bold yellow]")
        else:
             console.print("[bold green]Task deleted.[/bold green]")

def handle_clear(args):
    path = find_local_list_path()
    if not path:
        console.print(
            "No local pydo list found. Use `pydo init` to create one in the current directory."
        )
        return
    data = load_tasks(path)
    if len(data["tasks"]) == 0:
        console.print("No tasks in the current list. Create one by using `pydo add`.")
        return
    
    tasks_deleted_count = 0
    new_tasks = []
    for task in data["tasks"]: 
        
        with console.status(f"[bold green]Clearing task {task['description']}...", spinner="dots"):
            time.sleep(0.7)
       
        if not task["completed"]:
            new_tasks.append(task)
        else:
            tasks_deleted_count += 1

    if tasks_deleted_count > 0:
        data["tasks"] = new_tasks
        save_tasks(path, data)
        console.print(f"[bold green]List cleared of {tasks_deleted_count} tasks. [/bold green]")

# --- Main Entry Point & Argument Parsing ---
def run():
    parser = argparse.ArgumentParser(
        prog="pydo", description="A simple command-line todo list manager."
    )
    # This is a top-level flag that affects context for most sub-commands.
    parser.add_argument(
        "-g",
        "--global",
        action="store_true",
        help="Force operation on the global todo list.",
    )

    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Sub-command help"
    )

    # Command: init
    parser_init = subparsers.add_parser(
        "init", help="Initialize a local todo list in the current directory."
    )
    parser_init.set_defaults(func=handle_init)

    # Command: status
    parser_status = subparsers.add_parser(
        "status", help="Show the currently active list (local or global)."
    )
    parser_status.set_defaults(func=handle_status)

    # Command: list / ls
    parser_list = subparsers.add_parser("list", help="List tasks.", aliases=["ls"])
    parser_list.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Show all tasks, including completed ones.",
    )
    parser_list.add_argument(
        "--done", action="store_true", help="Show only completed tasks."
    )
    parser_list.set_defaults(func=handle_list)

    # Command: add
    parser_add = subparsers.add_parser("add", help="Add a new task.")
    parser_add.add_argument(
        "description", nargs="+", help="The description of the task."
    )
    parser_add.set_defaults(func=handle_add)

    # Command: done
    parser_done = subparsers.add_parser("done", help="Mark task(s) as done.")
    parser_done.add_argument(
        "task_ids",
        nargs="+",
        type=int,
        help="The ID(s) of the task(s) to mark as done.",
    )
    parser_done.set_defaults(func=handle_done)

    # Command: undone
    parser_undone = subparsers.add_parser("undone", help="Mark task(s) as not done.")
    parser_undone.add_argument(
        "task_ids",
        nargs="+",
        type=int,
        help="The ID(s) of the task(s) to mark as not done.",
    )
    parser_undone.set_defaults(func=handle_undone)

    # Command: edit
    parser_edit = subparsers.add_parser("edit", help="Edit a task.")
    parser_edit.add_argument("task_id", type=int, help="The ID of the task to edit.")
    parser_edit.add_argument(
        "new_description", nargs="+", help="The new description for the task."
    )
    parser_edit.set_defaults(func=handle_edit)

    # Command: remove / rm
    parser_remove = subparsers.add_parser(
        "remove", help="Remove task(s).", aliases=["rm"]
    )
    parser_remove.add_argument(
        "task_ids", nargs="+", type=int, help="The ID(s) of the task(s) to remove."
    )
    parser_remove.add_argument(
        "-f", "--force", action="store_true", help="Remove without confirmation."
    )
    parser_remove.set_defaults(func=handle_remove)

    # Command: clear
    parser_clear = subparsers.add_parser("clear", help="Remove all completed tasks.")
    parser_clear.add_argument(
        "-f", "--force", action="store_true", help="Clear without confirmation."
    )
    parser_clear.set_defaults(func=handle_clear)

    # --- Execution ---
    args = parser.parse_args(sys.argv[1:])
    
    if hasattr(args, "func"):
        args.func(args)


if __name__ == "__main__":
    run()
