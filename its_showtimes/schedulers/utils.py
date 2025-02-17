import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from json.decoder import JSONDecodeError


def authenticate(
        SCOPES: list[str] = ['https://www.googleapis.com/auth/calendar'],
        ) -> Credentials:
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time.
    if os.path.exists(".secret/token.json"):
        try:
            creds = Credentials.from_authorized_user_file(".secret/token.json")
        except JSONDecodeError as error:
            print(f'An error occurred while reading the token file. The token will be re-acquired: {error}')
            creds = None
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError as error:
                creds = None
                print(f'An error occurred while refreshing the token. The token will be re-acquired: {error}')
                flow = InstalledAppFlow.from_client_secrets_file(
                    ".secret/G_Cal_Creds.json", SCOPES)
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                ".secret/G_Cal_Creds.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(".secret/token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def delete_all_events_from_cal(google_cal_service,
                               cal_id: str,
                               ) -> None:
    
    print("STARTING DELETIONS!")
    
    page_token = None
    while True:
        events_result = google_cal_service.events().list(calendarId=cal_id, pageToken=page_token).execute()
        for event in events_result['items']:
            event_id = event['id']
            google_cal_service.events().delete(calendarId=cal_id, eventId=event_id).execute()
            print(f'DELETED EVENT: {event['summary']} AT {event['start']['dateTime']}')
        
        page_token = events_result.get('nextPageToken')
        if not page_token:
            break
    
    print("ENDING DELETIONS!\n\n")