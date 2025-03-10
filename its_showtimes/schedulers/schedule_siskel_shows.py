import datetime as dt

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import pickle

if not __name__ == '__main__':
    from schedulers.utils import authenticate, delete_all_events_from_cal
else:
    from utils import authenticate, delete_all_events_from_cal


def schedule_siskel_shows():

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
        if 'THE ROOM NEXT DOOR' in siskel_film_details_dict:
            siskel_film_details_dict['THE ROOM NEXT DOOR']['Runtime'] = 110
        
        if 'THE SEALED SOIL' in siskel_film_details_dict:
            siskel_film_details_dict['THE SEALED SOIL']['Runtime'] = 90
        
        if 'MYSTERY MOVIE MONDAY' in siskel_film_details_dict:
            siskel_film_details_dict['MYSTERY MOVIE MONDAY']['Runtime'] = 120

        for movie_title in siskel_showtimes_dict:
            # Skip movies that don't have a runtime specified.
            if 'Runtime' not in siskel_film_details_dict[movie_title]:
                print(f'RUNTIME MISSING FOR FILM "{movie_title}"')
                continue
            # Otherwise, proceed with creating events for the movie's showtimes.
            else:
                runtime = siskel_film_details_dict[movie_title]['Runtime']
                print(f'\nFilm: {movie_title}\t\tRuntime: {runtime} minutes')
                for showtime in siskel_showtimes_dict[movie_title]:
                    runtime_delta = dt.timedelta(minutes=runtime)
                    movie_start_str = showtime.strftime('%Y-%m-%dT%H:%M:%S')
                    movie_end = showtime + runtime_delta
                    movie_end_str = movie_end.strftime('%Y-%m-%dT%H:%M:%S')
                    # print(movie_title, runtime, movie_start_str, movie_end_str, sep='\t')

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

                    print("Show added:",
                          f'start={movie_start_str}', 
                          f'end={movie_end_str}', 
                          f'\tlink={event.get('htmlLink')}',
                           sep='\t')
                    # print(f"Event created: {movie_title} at {movie_start_str} \t\t {event.get('htmlLink')}\n")

    except HttpError as error:
        print("An error occurred:", error)
    

if __name__ == '__main__':
    schedule_siskel_shows()