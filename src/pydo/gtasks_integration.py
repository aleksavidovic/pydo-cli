import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleTasksClient:
    SCOPES = ["https://www.googleapis.com/auth/tasks"]

    def __init__(self):
        self._creds = None
        self._service = None
        self.tasks = None

    def authenticate(self):
        """Handles user authentication and token management."""
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", self.SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        self._creds = creds
        self._service = build("tasks", "v1", credentials=self._creds)

    def get_lists(self):
        if not self._service:
            print("Client not connected to the service. Authenticate and try again.")
            return

        try:
            results = self._service.tasklists().list().execute()
            task_lists = results.get("items", [])

            if not task_lists:
                print("No task list found on Google Tasks.")

            self._task_lists = task_lists
            print("Retreived lists: ")
            for task_list in self._task_lists:
                print(f" - {task_list['title']}")
        except Exception as e:
            print("Error while retreiving lists from Google Tasks: {e}")


    def get_tasks(self, service):
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

            self.tasks = items

            print("Upcoming tasks:")
            for item in items:
                # Print the task title and its ID
                print(f"  - {item['title']} (ID: {item['id']})")

        except HttpError as err:
            print(f"An error occurred: {err}")

