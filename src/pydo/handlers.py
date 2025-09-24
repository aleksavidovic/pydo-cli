import os
from pathlib import Path

from pydo import console
from pydo.models import PydoData
from pydo.pydo_list import PydoList
from pydo.views import (
    render_add_success,
    render_clear_success,
    render_complete_success,
    render_focus_success,
    render_hide_success,
    render_remove_success,
    render_uncomplete_success,
    render_unhide_success,
)

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
        if task.hidden:
            continue
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
    """
    Handler function for pydo `list` subcommand.

    If not given any additional args, it finds the
    nearest local .pydo directory with tasks.json
    file and prints them to the screen.

    Options are used for filtering tasks.

    A pygo -g / --global flag will make it look for a
    pydo list in the home directory
    """
    path = get_global_list_path() if args.is_global else find_local_list_path()
    if not path:
        print("No list found.")
        return

    pydo_list = PydoList(path)
    if args.focus:
        tasks = pydo_list.get_focused_tasks()
    else:
        tasks = pydo_list.get_tasks()
    tasks_md = pydo_list.get_metadata()

    print_tasks(
        tasks,
        tasks_md.total_completed_tasks,
        show_all=args.all,
        show_done=args.done,
        title=tasks_md.local_list_name,
    )


def handle_clearlist(args):
    """
    Clears the screen by sending an appropriate command
    directly to the system, according to the underlying OS.
    Then it calls handle_list and passes on the args.

    Used for better UX, so that a user gets a list
    printed on a clean screen without clutter and noise
    of previous terminal output
    """
    os.system("cls" if os.name == "nt" else "clear")
    handle_list(args)


def handle_add(args):
    path = get_global_list_path() if args.is_global else find_local_list_path()
    if not path:
        print("No list found")
        return

    description = " ".join(args.description).strip()
    pydo_list = PydoList(path)
    new_task = pydo_list.add_task(description)
    list_name = pydo_list.get_list_name()
    render_add_success(new_task, list_name)


def handle_focus(args):
    """
    Toggles focus field on task(s) for given ids.

    Focus is a local, aesthetic function, so toggle is ok.
    """
    path = get_global_list_path() if args.is_global else find_local_list_path()
    if not path:
        print("No list found")
        return

    pydo_list = PydoList(path)
    focus_on_count, focus_off_count = pydo_list.toggle_focus(args.task_ids)

    render_focus_success(focus_on_count, focus_off_count)


def handle_done(args):
    path = get_global_list_path() if args.is_global else find_local_list_path()
    if not path:
        print("No list found")
        return

    pydo_list = PydoList(path)
    completed_count, skipped_count = pydo_list.complete_tasks(args.task_ids)
    render_complete_success(completed_count, skipped_count)


def handle_undone(args):
    path = get_global_list_path() if args.is_global else find_local_list_path()
    if not path:
        print("No list found")
        return

    pydo_list = PydoList(path)
    uncompleted_count, skipped_count = pydo_list.uncomplete_tasks(args.task_ids)
    render_uncomplete_success(uncompleted_count, skipped_count)


def handle_hide(args):
    path = get_global_list_path() if args.is_global else find_local_list_path()
    if not path:
        print("No list found")
        return

    pydo_list = PydoList(path)
    hidden_count, skipped_count = pydo_list.hide_tasks(args.task_ids)
    render_hide_success(hidden_count, skipped_count)


def handle_unhide(args):
    path = get_global_list_path() if args.is_global else find_local_list_path()
    if not path:
        print("No list found")
        return

    pydo_list = PydoList(path)
    unhidden_count, skipped_count = pydo_list.unhide_tasks(args.task_ids)
    render_unhide_success(unhidden_count, skipped_count)


def handle_edit(args):
    console.print("[bold red]Edit function not implemented yet.[/bold red]")


def handle_remove(args):
    path = get_global_list_path() if args.is_global else find_local_list_path()
    if not path:
        print("No list found")
        return

    pydo_list = PydoList(path)
    removed_count, skipped_count = pydo_list.remove_tasks(args.task_ids)
    render_remove_success(removed_count, skipped_count)


def handle_clear(args):
    path = get_global_list_path() if args.is_global else find_local_list_path()
    if not path:
        print("No list found")
        return

    pydo_list = PydoList(path)
    cleared_count = pydo_list.clear_completed_tasks()
    render_clear_success(cleared_count)


def handle_sync(args):
    path = get_global_list_path() if args.is_global else find_local_list_path()
    if not path:
        print("No list found")
        return

    from pydo.gtasks_integration import GoogleTasksClient

    pydo_list = PydoList(path)
    gtasks_client = GoogleTasksClient()
    try:
        gtasks_client.authenticate()

        if pydo_list.get_list_google_id() == "":
            gtasks_list_id = gtasks_client.create_list(pydo_list.get_list_name())

            if gtasks_list_id:
                print("Google Tasks List created!")
                pydo_list.set_google_id(gtasks_list_id)
                # Since new list is created in Google Tasks, tasks flow in one direction
                # ONLY Pydo => GTasks
                # BUT !!! GTasks API returns Task IDs
                # I need to assign those IDs to pydo tasks
                # BUT BUT !!!!!
                # Let's see other cases and unify the sync mechanism if possible??
            else:
                raise Exception("Couldn't create new list")
        else:  # pydo list has a google id (but is it valid?)
            pass
    except Exception as e:
        print(f"Error syncing with Google Tasks: {e}")
