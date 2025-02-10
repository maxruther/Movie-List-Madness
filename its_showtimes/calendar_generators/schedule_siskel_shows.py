import os.path
import datetime as dt

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google.auth.exceptions import RefreshError

import pickle


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


def authenticate(
        SCOPES: list[str] = ['https://www.googleapis.com/auth/calendar'],
        ) -> Credentials:
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time.
    if os.path.exists(".secret/token.json"):
        creds = Credentials.from_authorized_user_file(".secret/token.json")
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError as error:
                creds = None
                print(f'An error occurred while refreshing the token. The token will be re-acquired: {error}')
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                ".secret/G_Cal_Creds.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(".secret/token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def main():

    creds = authenticate()
        
    try:
        service = build("calendar", "v3", credentials=creds)


        # # ATTENTION ATTENTION ATTENTION - Need to improve the Siskel scraper before proceeding.
        # raise Exception("I NEED TO CODE THE SISKEL SCRAPE so that it scrapes their films runtimes as well.")


        movie_radar_cal_id = '8b43bb1335dfcf5ae5bec565a51267c32d9a677cf134777510998bda8723c18c@group.calendar.google.com'

        delete_all_events_from_cal(service, movie_radar_cal_id)


        siskel_showtimes_dict = None
        with open('data/showtimes/siskel_films_showtimes_dict.pkl', 'rb') as file:
            siskel_showtimes_dict = pickle.load(file)

        siskel_film_details_dict = None
        with open('data/showtimes/siskel_films_details_dict.pkl', 'rb') as file:
            siskel_film_details_dict = pickle.load(file)
        
        # Some runtimes were missing from the Siskel page. I'm adding 
        # them manually here.
        siskel_showtimes_dict['THE ROOM NEXT DOOR']['Runtime'] = 110
        siskel_showtimes_dict['THE SEALED SOIL']['Runtime'] = 90
        siskel_showtimes_dict['MYSTERY MOVIE MONDAY']['Runtime'] = 120

        for movie_title in siskel_showtimes_dict:
            # Skip movies that don't have a runtime specified.
            if 'Runtime' not in siskel_film_details_dict[movie_title]:
                continue
            # Otherwise, proceed with creating events for the movie's showtimes.
            else:
                for showtime in siskel_showtimes_dict[movie_title]:
                    movie_runtime = siskel_film_details_dict[movie_title]['Runtime']
                    runtime_delta = dt.timedelta(minutes=movie_runtime)
                    movie_start_str = showtime.strftime('%Y-%m-%dT%H:%M:%S')
                    movie_end = showtime + runtime_delta
                    movie_end_str = movie_end.strftime('%Y-%m-%dT%H:%M:%S')
                    print(movie_title, movie_runtime, movie_start_str, movie_end_str, sep='\t')

                    event = {
                        "summary": movie_title,
                        "location": "164 N State St, Chicago, IL 60601",
                        "description": "Some more details on this awesome event",
                        "colorId": 5,
                        "start": {
                            "dateTime": movie_start_str,
                            "timeZone": "America/Chicago"
                        },
                        "end": {
                            "dateTime": movie_end_str,
                            "timeZone": "America/Chicago"
                        }
                    }
                    
                    event = service.events().insert(calendarId=movie_radar_cal_id, body=event).execute()

                    print(f"Event created: {movie_title} at {movie_start_str} \t\t {event.get('htmlLink')}\n")


    except HttpError as error:
        print("An error occurred:", error)
    

if __name__ == '__main__':
    main()