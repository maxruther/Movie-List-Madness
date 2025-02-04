import os.path
import datetime as dt

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import pickle

SCOPES = ['https://www.googleapis.com/auth/calendar']

def delete_all_events_from_cal(google_cal_service, cal_id: str):
    all_events_result = google_cal_service.events().list(calendarId=cal_id).execute()
    events = all_events_result.get("items", [])

    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        # print(f'Event ID: {event['id']}', f'Event Summary: {event["summary"]}', f'Event Start Time: {event['start']}', sep='\t')

        event_id = event['id']

        google_cal_service.events().delete(calendarId=cal_id, eventId=event_id).execute()
        print(f'DELETED EVENT: {event['summary']} AT {event['start']['dateTime']}')


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

        movie_radar_cal_id = 'd5608bfd7792dbbddee666bf5f63d6795af57083ecfc437f718df9018b0896b8@group.calendar.google.com'

        delete_all_events_from_cal(service, movie_radar_cal_id)

        """all_events_result = service.events().list(calendarId=movie_radar_cal_id).execute()
        events = all_events_result.get("items", [])

        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(f'Event ID: {event['id']}', f'Event Summary: {event["summary"]}', f'Event Start Time: {event['start']}', sep='\t')

            event_id = event['id']

            service.events().delete(calendarId=movie_radar_cal_id, eventId=event_id).execute()"""


        mb_showtimes_dict = None
        with open('musicbox_films_showtimes_dict.pkl', 'rb') as file:
            mb_showtimes_dict = pickle.load(file)

        mb_film_details_dict = None
        with open('musicbox_film_details_dict.pkl', 'rb') as file:
            mb_film_details_dict = pickle.load(file)


        for movie_title in mb_showtimes_dict:
            for showtime in mb_showtimes_dict[movie_title]:
                movie_runtime = mb_film_details_dict[movie_title]['Runtime']
                runtime_delta = dt.timedelta(minutes=movie_runtime)
                movie_start_str = showtime.strftime('%Y-%m-%dT%H:%M:%S')
                movie_end = showtime + runtime_delta
                movie_end_str = movie_end.strftime('%Y-%m-%dT%H:%M:%S')
                print(movie_title, movie_runtime, movie_start_str, movie_end_str, sep='\t')

                event = {
                    "summary": movie_title,
                    "location": "3733 N Southport Ave, Chicago, IL 60613",
                    "description": "Some more details on this awesome event",
                    "colorId": 6,
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

        # print(mb_film_details_dict['Legend'])

        # for showtime in mb_showtime_dict['Legend']:
        #     movie_runtime = mb_film_details_dict['Legend']['Runtime']
        #     runtime_delta = dt.timedelta(minutes=movie_runtime)
        #     movie_start_str = showtime.strftime('%Y-%m-%dT%H:%M:%S')
        #     movie_end = showtime + runtime_delta
        #     movie_end_str = movie_end.strftime('%Y-%m-%dT%H:%M:%S')
        #     print('Legend', movie_runtime, movie_start_str, movie_end_str, sep='\n')

        #     event = {
        #         "summary": "Legend",
        #         "location": "3733 N Southport Ave, Chicago, IL 60613",
        #         "description": "Some more details on this awesome event",
        #         "colorId": 6,
        #         "start": {
        #             "dateTime": movie_start_str,
        #             "timeZone": "America/Chicago"
        #         },
        #         "end": {
        #             "dateTime": movie_end_str,
        #             "timeZone": "America/Chicago"
        #         }
        #     }


        #     movie_radar_cal_id = 'd5608bfd7792dbbddee666bf5f63d6795af57083ecfc437f718df9018b0896b8@group.calendar.google.com'

        #     event = service.events().insert(calendarId=movie_radar_cal_id, body=event).execute()

        #     print(f"Event created {event.get('htmlLink')}")

    except HttpError as error:
        print("An error occurred:", error)
    

if __name__ == '__main__':
    main()