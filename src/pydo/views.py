from pydo import console
from pydo.models import Task


def render_add_success(task: Task, list_name: str):
    console.print(
        f"✅ Added: '[yellow]{task.description}[/yellow]' to your [blue]{list_name}[/blue] list."
    )


def render_focus_success(focus_on_count: int, focus_off_count: int):
    if focus_off_count > 0:
        console.print(
            f"Removed focus from [dim red]{focus_off_count}[/dim red] task{'s' if focus_off_count > 1 else ''}"
        )

    if focus_on_count > 0:
        console.print(
            f"Added focus on [dim blue]{focus_on_count}[/dim blue] task{'s' if focus_on_count > 1 else ''}"
        )


def render_complete_success(completed_count: int, skipped_count: int):
    if skipped_count == 0 and completed_count == 0:
        console.print("[dim]No tasks affected[/]")
        return
    if skipped_count > 0:
        console.print(
            f"Skipped [bold red]{skipped_count}[/] tasks (invalid id / already completed)."
        )
    if completed_count > 0:
        console.print(
            f"[bold green]Nice work! You've completed {completed_count} task{'s' if completed_count > 1 else ''}. 🎉[/bold green]"
        )


def render_uncomplete_success(uncompleted_count: int, skipped_count: int):
    if skipped_count == 0 and uncompleted_count == 0:
        console.print("[dim]No tasks affected[/]")
        return
    if skipped_count > 0:
        console.print(
            f"Skipped [bold red]{skipped_count}[/] tasks (invalid id / already pending)."
        )
    if uncompleted_count > 0:
        console.print(
            f"[bold yellow]Marked {uncompleted_count} task{'s' if uncompleted_count > 1 else ''} as not complete. [/]"
        )


def render_remove_success(removed_count: int, skipped_count: int):
    if skipped_count == 0 and removed_count == 0:
        console.print("[dim]No tasks affected[/]")
        return
    if skipped_count > 0:
        console.print(
            f"Skipped [bold red]{skipped_count}[/] tasks (invalid id / already pending)."
        )
    if removed_count > 0:
        console.print(
            f"[bold yellow]Removed {removed_count} task{'s' if removed_count > 1 else ''}. [/]"
        )


def render_hide_success(hidden_count: int, skipped_count: int):
    if skipped_count == 0 and hidden_count == 0:
        console.print("[dim]No tasks affected[/]")
        return
    if skipped_count > 0:
        console.print(
            f"Skipped [bold red]{skipped_count}[/] tasks (invalid id / already hidden)."
        )
    if hidden_count > 0:
        console.print(
            f"[bold yellow]Hidden {hidden_count} task{'s' if hidden_count > 1 else ''}. [/]"
        )


def render_unhide_success(unhidden_count: int, skipped_count: int):
    if skipped_count == 0 and unhidden_count == 0:
        console.print("[dim]No tasks affected[/]")
        return
    if skipped_count > 0:
        console.print(
            f"Skipped [bold red]{skipped_count}[/] tasks (invalid id / not hidden)."
        )
    if unhidden_count > 0:
        console.print(
            f"[bold yellow]Unhide {unhidden_count} task{'s' if unhidden_count > 1 else ''}. [/]"
        )


def render_clear_success(cleared_count: int):
    if cleared_count == 0:
        console.print("[dim]No tasks affected[/]")
        return

    console.print(
        f"[bold green]List cleared of {cleared_count} task{'s' if cleared_count > 0 else ''}. [/bold green]"
    )
