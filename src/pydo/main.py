import argparse
import sys

from pydo import handlers


def run():
    parser = argparse.ArgumentParser(
        prog="pydo", description="A simple command-line todo list manager."
    )
    # This is a top-level flag that affects context for most sub-commands.
    parser.add_argument(
        "-g",
        "--global",
        dest="is_global",
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
    parser_init.set_defaults(func=handlers.handle_init)

    parser_sync = subparsers.add_parser(
        "sync", help="Synchronize list with google tasks"
    )
    parser_sync.set_defaults(func=handlers.handle_sync)

    # Command: status
    parser_status = subparsers.add_parser(
        "status",
        help="Show the currently active list (local or global).",
        aliases=["st"],
    )
    parser_status.set_defaults(func=handlers.handle_status)

    # Command: list / ls
    parser_list = subparsers.add_parser("list", help="List tasks.", aliases=["ls", "l"])
    parser_list.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Show all tasks, including completed ones.",
    )
    parser_list.add_argument(
        "--done", action="store_true", help="Show only completed tasks."
    )
    parser_list.set_defaults(func=handlers.handle_list)

    # Command cls
    parser_clearlist = subparsers.add_parser(
        "cls", help="Clear screen and list tasks.", aliases=["c"]
    )
    parser_clearlist.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Show all tasks, including completed ones.",
    )
    parser_clearlist.add_argument(
        "--done", action="store_true", help="Show only completed tasks."
    )
    parser_clearlist.set_defaults(func=handlers.handle_clearlist)

    # Command: add
    parser_add = subparsers.add_parser("add", aliases=["a"], help="Add a new task.")
    parser_add.add_argument(
        "description", nargs="+", help="The description of the task."
    )
    parser_add.set_defaults(func=handlers.handle_add)

    parser_focus = subparsers.add_parser(
        "focus", aliases=["f"], help="Toggle focus on task(s)"
    )
    parser_focus.add_argument(
        "task_ids",
        nargs="+",
        type=int,
        help="The ID(s) of the task(s) to add focus to.",
    )
    parser_focus.set_defaults(func=handlers.handle_focus)
    # Command: done
    parser_done = subparsers.add_parser(
        "done", help="Mark task(s) as done.", aliases=["d"]
    )
    parser_done.add_argument(
        "task_ids",
        nargs="+",
        type=int,
        help="The ID(s) of the task(s) to mark as done.",
    )
    parser_done.set_defaults(func=handlers.handle_done)

    # Command hide
    parser_hide = subparsers.add_parser(
        "hide", help="Mark task(s) as hidden.", aliases=["h"]
    )
    parser_hide.add_argument(
        "task_ids",
        nargs="+",
        type=int,
        help="The ID(s) of the task(s) to mark as done.",
    )
    parser_hide.set_defaults(func=handlers.handle_hide)
    # Command: undone
    parser_undone = subparsers.add_parser(
        "undone", aliases=["u"], help="Mark task(s) as not done."
    )
    parser_undone.add_argument(
        "task_ids",
        nargs="+",
        type=int,
        help="The ID(s) of the task(s) to mark as not done.",
    )
    parser_undone.set_defaults(func=handlers.handle_undone)

    # Command: edit
    parser_edit = subparsers.add_parser("edit", help="Edit a task.", aliases=["e"])
    parser_edit.add_argument("task_id", type=int, help="The ID of the task to edit.")
    parser_edit.add_argument(
        "new_description", nargs="+", help="The new description for the task."
    )
    parser_edit.set_defaults(func=handlers.handle_edit)

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
    parser_remove.set_defaults(func=handlers.handle_remove)

    # Command: clear
    parser_clear = subparsers.add_parser("clear", help="Remove all completed tasks.")
    parser_clear.add_argument(
        "-f", "--force", action="store_true", help="Clear without confirmation."
    )
    parser_clear.set_defaults(func=handlers.handle_clear)

    # --- Execution ---
    args = parser.parse_args(sys.argv[1:])

    if hasattr(args, "func"):
        args.func(args)


if __name__ == "__main__":
    run()
