import os.path
import datetime as dt

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(".secret/G_Cal_Creds.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())
        
    try:
        service = build("calendar", "v3", credentials=creds)

        event = {
            "summary": "My Python Event",
            "location": "Somewhere Online",
            "description": "Some more details on this awesome event",
            "colorId": 6,
            "start": {
                "dateTime": "2025-01-21T09:00:00-06:00",
                "timeZone": "America/Chicago"
            },
            "end": {
                "dateTime": "2025-01-21T17:00:00-06:00",
                "timeZone": "America/Chicago"
            },
            "recurrence": [
                "RRULE:FREQ=DAILY;COUNT=3"
            ],
            "attendees": [
                {"email": "jacksleuther@gmail.com"},
            ]
        }


        movie_radar_cal_id = '8dcd03d973968a6d4ec717963c8272149446098425d040c8b9e22df80874f105@group.calendar.google.com'

        event = service.events().insert(calendarId=movie_radar_cal_id, body=event).execute()

        # service.calendars().delete(calendarId=movie_radar_cal_id).execute()


        # page_token = None
        # calendar_list = service.calendarList().list().execute()
        # print(calendar_list)
        # for calendar_list_entry in calendar_list['items']:
        #     print(calendar_list_entry)

        print(f"Event created {event.get('htmlLink')}")

        # Getting the next 10 events from my calendar
        """now = dt.datetime.now().isoformat() + "Z"

        event_result = service.events().list(calendarId="primary", timeMin=now, maxResults=10, singleEvents=True, orderBy="startTime").execute()
        events = event_result.get("items", [])

        if not events:
            print("No upcoming events found!")
            return
        
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])"""

    except HttpError as error:
        print("An error occurred:", error)
    

if __name__ == '__main__':
    main()