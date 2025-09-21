import json
import os
import time
import uuid
from pathlib import Path

from pydo import console
from pydo.models import PydoData, Task

PYDO_DIR = ".pydo"
PYDO_TASKS_FILENAME = "tasks.json"


# --- Context Resolution ---
def find_local_list_path():
    """
    Traverse up from the current directory to find a '.pydo' file/directory.
    Returns the Path object if found, otherwise None.
    """
    CWD = Path.cwd()
    HOME = Path.home()
    while CWD != HOME:
        if (CWD / PYDO_DIR / PYDO_TASKS_FILENAME).exists():
            return CWD / PYDO_DIR / PYDO_TASKS_FILENAME
        CWD = CWD.parent
    return None


def get_global_list_path():
    global_list_path = Path.home() / PYDO_DIR / PYDO_TASKS_FILENAME
    return global_list_path if global_list_path.exists() else None


# --- Helper Functions (Save / Load) ---
def save_tasks(path: Path, data: PydoData):
    with path.open("w") as f:
        f.write(data.model_dump_json(indent=2))


def load_tasks(path: Path) -> PydoData:
    if not path.exists():
        return PydoData()
    with path.open("r") as f:
        return PydoData.model_validate(json.load(f))


def print_tasks(tasks, total_completed, show_all=False, show_done=True, title=""):
    from rich.table import Table

    caption = f"[normal]Total tasks done: [green]{total_completed}[/]"
    table = Table(
        title=title,
        title_style="bold green",
        caption=caption,
        caption_style="",
        highlight=True,
        show_lines=False,
    )
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center", style="magenta")
    table.add_column("Description")

    for id, task in enumerate(tasks, 1):
        display_id = f"[green]{id}[/]" if task.completed else f"{id}"
        status = "[green]✅[/]" if task.completed else "[red]❌[/red]"
        desc_not_done_style = "yellow"
        if task.focus is not None and not task.completed:
            if task.focus:
                status = "[bold blue]▶️[/bold blue]"
                desc_not_done_style = "bold blue"
        description_text = task.description
        description = (
            f"[green strike]{description_text}[/]"
            if task.completed
            else f"[{desc_not_done_style}]{description_text}[/{desc_not_done_style}]"
        )
        # style = "green strike dim" if task.completed else "yellow"
        table.add_row(display_id, status, description)  # , style=style)

    console.print(table)


# --- CLI Command Handlers ---
def handle_init(args):
    CWD = Path.home() if args.is_global else Path.cwd()
    tasks_path = CWD / PYDO_DIR / PYDO_TASKS_FILENAME

    if tasks_path.is_file():
        console.print(f"pydo already initialized in {CWD}")
        return
    suggested_name = str(Path.cwd().name) if not args.is_global else "Pydo Global List"
    chosen_name = input(f"Pydo list name (default: {suggested_name}): ").strip()
    if chosen_name == "":
        chosen_name = suggested_name

    from pydo.art import run_init_animation

    run_init_animation()

    console.print(f"Creating pydo directory at {CWD}...")
    try:
        (CWD / PYDO_DIR).mkdir(exist_ok=True)
    except FileExistsError as e:
        console.print(f"[red]{e}[/red]")
        console.print(
            f"A file named {PYDO_DIR} exists at {CWD}. Can't create directory with name {PYDO_DIR}"
        )
        console.print(f"Deleted the file {CWD / PYDO_DIR} and try initializing again.")
        return

    console.print(f"Creating tasks file at {tasks_path}...")
    initial_data = PydoData()
    initial_data.metadata.local_list_name = chosen_name
    tasks_path.write_text(initial_data.model_dump_json(indent=2))

    console.print(f"🎉 Successfully initialized pydo list in {CWD}")


def handle_status(args):
    if args.is_global:
        global_path = get_global_list_path()
        if global_path is None:
            console.print(
                "No global list present. Create global list with [yellow]pydo --global init[/yellow]"
            )
            return
        else:
            console.print(f"- Active list: Global ({global_path.parent})")
            return

    local_path = find_local_list_path()
    if local_path is None:
        global_path = get_global_list_path()
        if global_path is None:
            console.print(
                "No local or global list is active. Create a list with [yellow]pydo [-g] init[/yellow]"
            )
            return
        else:
            console.print(f"- Active list: Global ({global_path.parent})")
    else:
        console.print(f"- Active list: Local ({local_path.parent})")


def handle_list(args):
    if args.is_global:
        path = get_global_list_path()
        if path is None:
            console.print("No global list found.")
            console.print("Create one with [yellow]pydo --global init[/yellow]")
            return
        else:
            data = load_tasks(path)
            print_tasks(
                data.tasks,
                data.metadata.total_completed_tasks,
                show_all=args.all,
                show_done=args.done,
                title=data.metadata.local_list_name,
            )
            return

    path = find_local_list_path()
    if path is None:
        console.print("No local list found.")
        path = get_global_list_path()
        if path is None:
            console.print("No global list found.")
            console.print(
                "No local or global list found. Create a new list using [yellow]pydo [-g] init[/yellow]"
            )
            return

    data = load_tasks(path)
    print_tasks(
        data.tasks,
        data.metadata.total_completed_tasks,
        show_all=args.all,
        show_done=args.done,
        title=data.metadata.local_list_name,
    )


def handle_clearlist(args):
    os.system("cls" if os.name == "nt" else "clear")
    handle_list(args)


def handle_add(args):
    if args.is_global:
        path = get_global_list_path()
        if path is None:
            console.log("No global list found.")
            return
        list_name = "global"
    else:
        path = find_local_list_path()
        if path is None:
            console.log("No local list found.")
            return
        list_name = "local"

    try:
        data = load_tasks(path)
    except FileNotFoundError:
        console.print(
            f"Task creation failed. Are you sure pydo is initialized here ({path})?"
        )
        return
    description = " ".join(args.description)
    new_task = Task(id=uuid.uuid4(), description=description, completed=False)
    data.tasks.append(new_task)
    save_tasks(path, data)
    console.print(
        f"✅ Added: '[yellow]{description}[/yellow]' to your [blue]{list_name}[/blue] list."
    )


def handle_focus(args):
    if args.is_global:
        path = get_global_list_path()
        if path is None:
            console.log("No global list found.")
            return
    else:
        path = find_local_list_path()
        if path is None:
            console.print(
                "No local pydo list found. Use `pydo init` to create one in the current directory."
            )
            return

    data = load_tasks(path)
    if len(data.tasks) == 0:
        console.print("No tasks in the current list. Create one by using `pydo add`.")
        return

    tasks_focused_count = 0
    tasks_unfocused_count = 0
    for task_id in sorted(list(set(args.task_ids))):  # Sort and de-duplicate IDs
        if (task_id - 1) < 0 or task_id > len(data.tasks):
            console.print(
                f"[bold red]Error:[/] Task ID {task_id} is invalid. Skipping."
            )
            continue

        task = data.tasks[task_id - 1]

        if task.focus is not None:
            if task.focus:
                task.focus = False
                tasks_unfocused_count += 1
            else:
                task.focus = True
                tasks_focused_count += 1
        else:
            task.focus = True
            tasks_focused_count += 1

    if tasks_focused_count > 0:
        console.print(
            f"Added focus on [dim blue]{tasks_focused_count}[/dim blue] task{'s' if tasks_focused_count > 1 else ''}"
        )

    if tasks_unfocused_count > 0:
        console.print(
            f"Removed focus from [dim red]{tasks_unfocused_count}[/dim red] task{'s' if tasks_unfocused_count > 1 else ''}"
        )

    if tasks_focused_count > 0 or tasks_unfocused_count > 0:
        save_tasks(path, data)


def handle_done(args):
    if args.is_global:
        path = get_global_list_path()
        if path is None:
            console.log("No global list found.")
            return
    else:
        path = find_local_list_path()
        if path is None:
            console.print(
                "No local pydo list found. Use `pydo init` to create one in the current directory."
            )
            return

    data = load_tasks(path)
    if len(data.tasks) == 0:
        console.print("No tasks in the current list. Create one by using `pydo add`.")
        return

    tasks_completed_count = 0

    for task_id in sorted(list(set(args.task_ids))):  # Sort and de-duplicate IDs
        if (task_id - 1) < 0 or task_id > len(data.tasks):
            console.print(
                f"[bold red]Error:[/] Task ID {task_id} is invalid. Skipping."
            )
            continue

        task = data.tasks[task_id - 1]

        if task.completed:
            console.print(
                f"Task {task_id}: '[yellow]{task.description}[/yellow]' is already done."
            )
            continue

        with console.status(
            f"[bold green]Completing task {task_id}...", spinner="dots"
        ):
            # This sleep makes the animation feel more deliberate
            time.sleep(0.7)
            task.completed = True
            tasks_completed_count += 1

        console.print(f"✅[strike dim green]{task.description}[/strike dim green]")

    # 3. Save the data back to the file if changes were made
    if tasks_completed_count > 0:
        data.metadata.total_completed_tasks += tasks_completed_count
        save_tasks(path, data)
        if tasks_completed_count > 1:
            console.print(
                f"\n[bold green]Nice work! You've completed {tasks_completed_count} tasks. 🎉[/bold green]"
            )
        else:
            console.print("[bold green]Nice work! 🎉[/bold green]")


def handle_undone(args):
    if args.is_global:
        path = get_global_list_path()
        if path is None:
            console.log("No global list found.")
            return
    else:
        path = find_local_list_path()
        if path is None:
            console.print(
                "No local pydo list found. Use `pydo init` to create one in the current directory."
            )
            return
    data = load_tasks(path)
    if len(data.tasks) == 0:
        console.print("No tasks in the current list. Create one by using `pydo add`.")
        return

    tasks_uncompleted_count = 0
    for task_id in sorted(list(set(args.task_ids))):  # Sort and de-duplicate IDs
        if (task_id - 1) < 0 or task_id > len(data.tasks):
            console.print(
                f"[bold red]Error:[/] Task ID {task_id} is invalid. Skipping."
            )
            continue

        task = data.tasks[task_id - 1]

        if not task.completed:
            console.print(
                f"Task {task_id}: '[yellow]{task.description}[/yellow]' is already not completed."
            )
            continue

        with console.status(
            f"[bold yellow]Reverting task status {task_id}...", spinner="dots"
        ):
            # This sleep makes the animation feel more deliberate
            time.sleep(0.7)
            task.completed = False
            tasks_uncompleted_count += 1

        console.print(f"[strike dim yellow]{task.description}[/strike dim yellow]")
        # 3. Save file and report progress

    if tasks_uncompleted_count > 0:
        data.metadata.total_completed_tasks -= tasks_uncompleted_count
        save_tasks(path, data)
        if tasks_uncompleted_count > 1:
            console.print(
                f"\n[bold yellow]You've changed {tasks_uncompleted_count} tasks back to not complete. Go get them! [/bold yellow]"
            )
        else:
            console.print("[bold green]Task back in todo. Go get it![/bold green]")


def handle_edit(args):
    console.print("[bold red]Edit function not implemented yet.[/bold red]")


def handle_remove(args):
    if args.is_global:
        path = get_global_list_path()
        if path is None:
            console.log("No global list found.")
            return
    else:
        path = find_local_list_path()
        if path is None:
            console.print(
                "No local pydo list found. Use `pydo init` to create one in the current directory."
            )
            return
    data = load_tasks(path)
    if len(data.tasks) == 0:
        console.print("No tasks in the current list. Create one by using `pydo add`.")
        return

    tasks_deleted_count = 0
    for task_id in sorted(list(set(args.task_ids))):  # Sort and de-duplicate IDs
        if (task_id - 1) < 0 or task_id > len(data.tasks):
            console.print(
                f"[bold red]Error:[/] Task ID {task_id} is invalid. Skipping."
            )
            continue

        with console.status(
            f"[bold yellow]Removing task [strike dim green]{task_id}[/]...",
            spinner="dots",
        ):
            # This sleep makes the animation feel more deliberate
            time.sleep(0.7)

            del data.tasks[task_id - 1]
            tasks_deleted_count += 1

    if tasks_deleted_count > 0:
        save_tasks(path, data)
        if tasks_deleted_count > 1:
            console.print(
                f"\n[bold yellow]You've deleted {tasks_deleted_count} tasks. [/bold yellow]"
            )
        else:
            console.print("[bold green]Task deleted.[/bold green]")


def handle_clear(args):
    if args.is_global:
        path = get_global_list_path()
        if path is None:
            console.log("No global list found.")
            return
    else:
        path = find_local_list_path()
        if path is None:
            console.print(
                "No local pydo list found. Use `pydo init` to create one in the current directory."
            )
            return
    data = load_tasks(path)
    if len(data.tasks) == 0:
        console.print("No tasks in the current list. Create one by using `pydo add`.")
        return

    tasks_deleted_count = 0
    new_tasks = []
    for task in data.tasks:
        with console.status(
            f"[bold green]Clearing task {task.description}...", spinner="dots"
        ):
            time.sleep(0.7)

        if not task.completed:
            new_tasks.append(task)
        else:
            tasks_deleted_count += 1

    if tasks_deleted_count > 0:
        data.tasks = new_tasks
        save_tasks(path, data)
        console.print(
            f"[bold green]List cleared of {tasks_deleted_count} tasks. [/bold green]"
        )


def handle_sync(args):
    if args.is_global:
        path = get_global_list_path()
        if path is None:
            console.log("No global list found.")
            return
    else:
        path = find_local_list_path()
        if path is None:
            console.print(
                "No local pydo list found. Use `pydo init` to create one in the current directory."
            )
            return
    data = load_tasks(path)

    if data.metadata.local_list_name == "":
        print("Can't upload a list without a name.")
        suggested_name = Path.cwd().name
        new_name = input(
            f"Give name to current list before sync (Enter for default: {suggested_name})"
        ).strip()
        data.metadata.local_list_name = suggested_name if new_name == "" else new_name
    if (
        data.metadata.google_tasks_list_id == ""
    ):  # List not created yet on G Tasks => Create it now
        from pydo.gtasks_integration import GoogleTasksClient

        gtasks_client = GoogleTasksClient()
        try:
            gtasks_client.authenticate()
            gtasks_list_id = gtasks_client.create_list(data.metadata.local_list_name)
            if gtasks_list_id:
                print("Google Tasks List created!")
                data.metadata.google_tasks_list_id = gtasks_list_id
                tasks = [task.description for task in data.tasks]
                for task in tasks:
                    resp = gtasks_client.create_task(
                        task_list_id=gtasks_list_id, task_title=task
                    )
                save_tasks(path, data)
        except Exception as e:
            print(f"Error syncing with Google Tasks: {e}")
    else:
        print(
            "List already has google tasks id"
        )  # TODO => OK FOR NOW, NEED TO ACTUALLY CHECK IF ID MAPS TO A GTASKS LIST
