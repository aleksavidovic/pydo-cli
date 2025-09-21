from os import wait
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class NotAuthenticatedError(Exception):
    pass

class ClientNotSynchronisedError(Exception):
    pass

CREDENTIALS_PATH = "/home/alexv/Projects/pydo/src/pydo/credentials.json" # TODO: MOVE TO ENV AND RESEARCH HOW TO MANAGE THIS FOR DISTRIBUTION

class GoogleTasksClient:
    SCOPES = ["https://www.googleapis.com/auth/tasks"]

    def __init__(self):
        self._creds = None
        self._service = None
        self._is_synced: bool = False
        self._task_lists = []
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
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, self.SCOPES)
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
            self._is_synced = True
            print("Retreived lists: ")
            for idx, task_list in enumerate(self._task_lists):
                print(f" {idx+1} - {task_list['title']}")
        except Exception as e:
            print("Error while retreiving lists from Google Tasks: {e}")

    def create_list(self, list_name: str) -> str | None:
        if not self._service:
            raise NotAuthenticatedError("Client not connected to the service. Authenticate and try again.")

        new_list = {"title": list_name}
        try:
            response = self._service.tasklists().insert(body=new_list).execute() # TODO: Handle interpreting the response value
        except Exception as e:
            print(f"Error while trying to create Google Tasks list: {e}")
            return None
        if response:
            print(f"List created successfully! Google Tasks List id: {response.get('id')}")
            return response.get('id')


    def get_tasks(self, task_list_idx: int):
        """Prints the user's tasks from the primary task list."""
        if not self._service:
            raise NotAuthenticatedError("Client not connected to the service. Authenticate and try again.")
        if not self._is_synced:
            raise ClientNotSynchronisedError("Client not synchronised with Google Tasks. Synchronise to obtain task lists and tasks.")
        if type(task_list_idx) is not int or task_list_idx < 1 or task_list_idx > len(self._task_lists):
            raise KeyError("Invalid list number provided")

        task_list_id = self._task_lists[task_list_idx-1].get("id")
        if not task_list_id:
            raise KeyError("List doesn't have Google API id.")

        try:
            # Call the Tasks API
            results = (
                self._service.tasks().list(tasklist=task_list_id, showCompleted=False).execute()
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

