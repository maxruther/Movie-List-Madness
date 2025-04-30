import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from json.decoder import JSONDecodeError

import pandas as pd

from datetime import datetime


def authenticate(
        SCOPES: list[str] = ['https://www.googleapis.com/auth/calendar'],
        token_path: str = ".secret/token.json",
        creds_path: str = ".secret/G_Cal_Creds.json",
        ) -> Credentials:
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time.
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path)
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
                    creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds

def get_showtime_df_from_cal(
          service,
          test_cal_id: str,
          ) -> pd.DataFrame:
    

    scheduled_shows = []
    page_token = None
    while True:
        pages_event_results = service.events().list(calendarId=test_cal_id, pageToken=page_token).execute()

        pages_events = pages_event_results.get('items', [])

        for event in pages_events:
            show_title = event['summary']
            show_start = event['start']['dateTime']
            show_start_dttime = datetime.fromisoformat(show_start).astimezone()
            show_start_dttime_naive = show_start_dttime.replace(tzinfo=None)


            show_record = {
                    "Title": show_title,
                    "Showtime": show_start_dttime_naive,
                    }
            # print(show_record)

            scheduled_shows.append(show_record)

        page_token = pages_event_results.get('nextPageToken')
        if not page_token:
            break
    
    cal_showtime_df = pd.DataFrame(scheduled_shows)
    
    return cal_showtime_df
    



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


def get_show_info(
        film_title: str,
        film_year: str,
        film_director: str,
        info_df: pd.DataFrame,
        ) -> dict[str, str | int]:
    """Returns a dictionary of the show info for a given film title, 
    year, and director."""

    # Identify which dataset of show info this is, Siskel or Metacritic.
    info_df_name = None
    if 'Metascore' in info_df.columns:
        info_df_name = 'mc_info'
        title_attr = 'Title Searched'
        year_attr = 'Year Searched'
        director_attr = 'Director Searched'
    elif 'Meta' in info_df.columns:
        info_df_name = 'siskel_show_info'
        title_attr = 'Title'
        year_attr = 'Year'
        director_attr = 'Director'
    elif 'Format' in info_df.columns:
        info_df_name = 'musicbox_show_info'
        title_attr = 'Title'
        year_attr = 'Year'
        director_attr = 'Director'
    
    search_cond_mask = \
        (info_df[title_attr] == film_title) & \
        (info_df[year_attr] == film_year) & \
        (info_df[director_attr] == film_director)

    matching_info_df = info_df[search_cond_mask]
    # print(matching_info_df)

    if matching_info_df.empty:
        print(f"No '{info_df_name}' match found for {film_title} ({film_year}) by {film_director}")
        return None
        
        # raise Exception(f'ERROR: No \'siskel_info\' match found for {film_title} ({film_year}) by {film_director}')

    elif len(matching_info_df) > 1:
        raise Exception(
            f"ERROR: Multiple '{info_df_name}' matches found for {film_title} ({film_year}) by {film_director}",
            matching_info_df,
            sep='\n\n')


    matching_info_dict = matching_info_df.to_dict(orient='records')[0]

    return matching_info_dict