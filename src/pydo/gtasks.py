"""An example of a a simple integration with Google Tasks using OAuth flow"""

import argparse
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# The SCOPES define the level of access you are requesting.
# For tasks, readonly is not enough if you want to complete them.
SCOPES = ["https://www.googleapis.com/auth/tasks"]


def authenticate():
    """Handles user authentication and token management."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def list_tasks(service):
    """Prints the user's tasks from the primary task list."""
    try:
        # Call the Tasks API
        results = (
            service.tasks().list(tasklist="@default", showCompleted=False).execute()
        )
        items = results.get("items", [])

        if not items:
            print("No upcoming tasks found.")
            return

        print("Upcoming tasks:")
        for item in items:
            # Print the task title and its ID
            print(f"  - {item['title']} (ID: {item['id']})")

    except HttpError as err:
        print(f"An error occurred: {err}")


def complete_task(service, task_id):
    """Marks a specific task as completed."""
    try:
        # First, get the task to make sure it exists
        task = service.tasks().get(tasklist="@default", task=task_id).execute()

        # Update the task status to 'completed'
        task["status"] = "completed"

        result = (
            service.tasks()
            .update(tasklist="@default", task=task_id, body=task)
            .execute()
        )

        print(f"✅ Task '{result['title']}' marked as completed.")

    except HttpError as err:
        print(f"An error occurred: {err}")
        print("Please ensure the Task ID is correct.")


def main():
    """Main function to parse arguments and call the appropriate function."""
    parser = argparse.ArgumentParser(
        description="A simple command-line interface for Google Tasks."
    )
    parser.add_argument("--list", action="store_true", help="List all active tasks.")
    parser.add_argument(
        "--complete",
        type=str,
        metavar="TASK_ID",
        help="Mark a task as complete using its ID.",
    )

    args = parser.parse_args()

    creds = authenticate()
    service = build("tasks", "v1", credentials=creds)

    if args.list:
        list_tasks(service)
    elif args.complete:
        complete_task(service, args.complete)
    else:
        # Default action if no arguments are given
        print("No action specified. Use --list or --complete. Defaulting to list:")
        list_tasks(service)


if __name__ == "__main__":
    main()
