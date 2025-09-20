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

    # Command: status
    parser_status = subparsers.add_parser(
        "status", help="Show the currently active list (local or global)."
    )
    parser_status.set_defaults(func=handlers.handle_status)

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
    parser_list.set_defaults(func=handlers.handle_list)

    # Command cls
    parser_clearlist = subparsers.add_parser("cls", help="Clear screen and list tasks.")
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
    parser_add = subparsers.add_parser("add", help="Add a new task.")
    parser_add.add_argument(
        "description", nargs="+", help="The description of the task."
    )
    parser_add.set_defaults(func=handlers.handle_add)

    parser_done = subparsers.add_parser("focus", help="Toggle focus on task(s)")
    parser_done.add_argument(
        "task_ids",
        nargs="+",
        type=int,
        help="The ID(s) of the task(s) to add focus to.",
    )
    parser_done.set_defaults(func=handlers.handle_focus)
    # Command: done
    parser_done = subparsers.add_parser("done", help="Mark task(s) as done.")
    parser_done.add_argument(
        "task_ids",
        nargs="+",
        type=int,
        help="The ID(s) of the task(s) to mark as done.",
    )
    parser_done.set_defaults(func=handlers.handle_done)

    # Command: undone
    parser_undone = subparsers.add_parser("undone", help="Mark task(s) as not done.")
    parser_undone.add_argument(
        "task_ids",
        nargs="+",
        type=int,
        help="The ID(s) of the task(s) to mark as not done.",
    )
    parser_undone.set_defaults(func=handlers.handle_undone)

    # Command: edit
    parser_edit = subparsers.add_parser("edit", help="Edit a task.")
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
