import datetime as dt

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import pickle

if not __name__ == '__main__':
    from schedulers.utils import authenticate, delete_all_events_from_cal
else:
    from utils import authenticate, delete_all_events_from_cal


def schedule_musicbox_shows():

    creds = authenticate()
        
    try:
        service = build("calendar", "v3", credentials=creds)

        movie_radar_cal_id = 'd5608bfd7792dbbddee666bf5f63d6795af57083ecfc437f718df9018b0896b8@group.calendar.google.com'

        delete_all_events_from_cal(service, movie_radar_cal_id)

        
        mb_showtimes_dict = None
        with open('data/showtimes/musicbox_films_showtimes_dict.pkl', 'rb') as file:
            mb_showtimes_dict = pickle.load(file)

        mb_film_details_dict = None
        with open('data/showtimes/musicbox_film_details_dict.pkl', 'rb') as file:
            mb_film_details_dict = pickle.load(file)


        for movie_title in mb_showtimes_dict:
            if 'Runtime' not in mb_film_details_dict[movie_title]:
                print(f'RUNTIME MISSING FOR FILM "{movie_title}"')
                continue
            else:
                runtime = mb_film_details_dict[movie_title]['Runtime']
                print(f'\nFilm: {movie_title}\t\tRuntime: {runtime} minutes')
                for showtime in mb_showtimes_dict[movie_title]:
                    runtime_delta = dt.timedelta(minutes=runtime)
                    movie_start_str = showtime.strftime('%Y-%m-%dT%H:%M:%S')
                    movie_end = showtime + runtime_delta
                    movie_end_str = movie_end.strftime('%Y-%m-%dT%H:%M:%S')

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

                    print("Show added:",
                          f'start={movie_start_str}', 
                          f'end={movie_end_str}', 
                          f'\tlink={event.get('htmlLink')}',
                           sep='\t')
                    # print(f"Event created: {movie_title} at {movie_start_str} \t\t {event.get('htmlLink')}\n")

    except HttpError as error:
        print("An error occurred:", error)
    

if __name__ == '__main__':
    schedule_musicbox_shows()