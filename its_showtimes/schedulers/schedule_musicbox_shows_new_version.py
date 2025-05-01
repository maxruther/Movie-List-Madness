import datetime as dt

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import pickle

import pandas as pd

from datetime import datetime, date

if __name__ == '__main__':
    from utils import authenticate, delete_all_events_from_cal, get_show_info, get_showtime_df_from_cal
else:
    try:
        from utils import authenticate, delete_all_events_from_cal, get_show_info, get_showtime_df_from_cal
    except:
        try:
            from its_showtimes.schedulers.utils import authenticate, delete_all_events_from_cal, get_show_info, get_showtime_df_from_cal
        except:
            try:
                from schedulers.utils import authenticate, delete_all_events_from_cal, get_show_info, get_showtime_df_from_cal
            except:
                try:
                    from ..schedulers.utils import authenticate, delete_all_events_from_cal, get_show_info, get_showtime_df_from_cal
                except:
                    raise Exception("\n'schedule_musicbox_shows' ERROR: Failed to import all methods 'authenticate, delete_all_events_from_cal, get_show_info, get_showtime_df_from_cal'\n")

def insert_events_of_mb_shows(
        mb_showtimes_df,
        mb_info_df,
        mc_scrape_df,
        service,
        movie_radar_cal_id,
        ):

    for _ , row in mb_showtimes_df.iterrows():
            film_title = row['Title']
            film_year = row['Year']
            film_director = row['Director']
            showtime = row['Showtime'].to_pydatetime()
            # print(film_title, film_year, film_director, showtime, sep='\n')

            this_films_info_musicbox = get_show_info(
                film_title, film_year, film_director,
                mb_info_df
                )
            
            this_films_info_mc = get_show_info(
                film_title, film_year, film_director,
                mc_scrape_df
                )

            # Initialize the movie's event description and runtime.
            movie_event_desc = None
            runtime = None
            if this_films_info_musicbox:

                runtime = int(this_films_info_musicbox.get("Runtime", "120"))
                
                movie_event_desc_header = \
                    f'{film_year} | ' + \
                    f'{str(runtime)} min.'

                if this_films_info_mc:
                    metascore = this_films_info_mc.get('Metascore', None)
                    if metascore:
                        movie_event_desc_header += f' | {metascore}'
                
                if pd.notna(this_films_info_musicbox["Format"]):
                    movie_event_desc_header += f' | {this_films_info_musicbox["Format"]}'

                movie_event_desc = \
                    movie_event_desc_header + \
                    '\n\n' + \
                    f'Director(s): {film_director}' + \
                    '\n' + \
                    f'Writers: {this_films_info_musicbox["Writer"]}' + \
                    '\n' + \
                    f'Cast: {this_films_info_musicbox["Cast"]}'
                
            elif this_films_info_mc:

                runtime = int(this_films_info_mc['Runtime'])

                movie_event_desc = \
                    f'{this_films_info_mc["Year"]} | ' + \
                    f'{this_films_info_mc["Runtime"]} min. | ' + \
                    f'{this_films_info_mc.get("Metascore", 'N/A')}' + \
                    '\n\n' + \
                    f'Directed by: {this_films_info_mc["Directors"]}' + \
                    '\n' + \
                    f'Written by: {this_films_info_mc["Writers"]}' + \
                    '\n\n' + \
                    f'{this_films_info_mc["Summary"]}'
                
            else:
                movie_event_desc = 'No details available. Runtime set to ' \
                '120-minute default.'

                runtime = 120
            

            # Calculate the show's end time from its start time and runtime.
            runtime_delta = dt.timedelta(minutes=runtime)
            movie_start_str = showtime.strftime('%Y-%m-%dT%H:%M:%S')
            movie_end = showtime + runtime_delta
            movie_end_str = movie_end.strftime('%Y-%m-%dT%H:%M:%S')
            # print(film_title, runtime, movie_start_str, movie_end_str, sep='\t')
            # print(movie_event_desc, '\n\n')

            # Construct the event object for insertion into the calendar.
            event = {
                "summary": film_title,
                "location": "164 N State St, Chicago, IL 60601",
                "description": movie_event_desc,
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

            # Acknowledge the addition of the show to the calendar.
            print(f"Event created: {film_title} at {movie_start_str} \t\t {event.get('htmlLink')}\n")
    
    return


def schedule_musicbox_shows(
        mb_showtimes_df: pd.DataFrame,
        mb_info_df: pd.DataFrame,
        mc_scrape_df: pd.DataFrame,
        ):

    creds = authenticate()
        
    try:
        service = build("calendar", "v3", credentials=creds)

        movie_radar_cal_id = 'd5608bfd7792dbbddee666bf5f63d6795af57083ecfc437f718df9018b0896b8@group.calendar.google.com'

        # delete_all_events_from_cal(service, movie_radar_cal_id)

        already_scheduled_shows_df = get_showtime_df_from_cal(service, movie_radar_cal_id)

        new_shows_df = pd.merge(
            mb_showtimes_df, already_scheduled_shows_df,
            how='left', on=['Title', 'Showtime'], indicator=True,
            ).query('_merge == "left_only"').drop(columns=['_merge'])

        insert_events_of_mb_shows(new_shows_df, mb_info_df, mc_scrape_df, service, movie_radar_cal_id)


    except HttpError as error:
        print("An error occurred:", error)
    

if __name__ == '__main__':

    mb_showtimes_df = None
    with open('data/pkl/musicbox/musicbox_showtimes.pkl', 'rb') as file:
        mb_showtimes_df = pickle.load(file)

    mb_info_df = None
    with open('data/pkl/musicbox/musicbox_show_info.pkl', 'rb') as file:
        mb_info_df = pickle.load(file)

    mc_scrape_df = None
    with open('data/pkl/musicbox/mc_scrape/musicbox_show_info_mc_info.pkl', 'rb') as file:
        mc_scrape_df = pickle.load(file)

    # today = date.today()
    # n_days_of_shows_to_slate = dt.timedelta(days=2)
    # test_show_df = mb_showtimes_df[mb_showtimes_df['Showtime_Date'] >= today & mb_showtimes_df['Showtime_Date'] <= today + n_days_of_shows_to_slate]

    schedule_musicbox_shows(mb_showtimes_df, mb_info_df, mc_scrape_df)
