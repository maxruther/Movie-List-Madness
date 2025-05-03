import datetime as dt

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import pickle

import pandas as pd

if __name__ == '__main__':
    from utils import authenticate, delete_all_events_from_cal, get_show_info, get_showtime_df_from_cal, delete_upcoming_events_from_cal
else:
    try:
        from its_showtimes.schedulers.utils import authenticate, delete_all_events_from_cal, get_show_info, get_showtime_df_from_cal, delete_upcoming_events_from_cal
    except:
        try:
            from schedulers.utils import authenticate, delete_all_events_from_cal, get_show_info, get_showtime_df_from_cal, delete_upcoming_events_from_cal
        except:
            raise Exception("\n'schedule_siskel_shows' ERROR: Failed to import all methods 'authenticate, delete_all_events_from_cal, get_show_info'\n")


def insert_events_of_siskel_shows(
        siskel_showtimes_df,
        siskel_info_df,
        mc_scrape_df,
        service,
        movie_radar_cal_id,
        ):
    
    for _ , row in siskel_showtimes_df.iterrows():
        film_title = row['Title']
        film_year = row['Year']
        film_director = row['Director']
        showtime = row['Showtime'].to_pydatetime()
        # print(film_title, film_year, film_director, showtime, sep='\n')

        siskel_film_info_dict = get_show_info(
            film_title, film_year, film_director,
            siskel_info_df
            )
        
        mc_film_info_dict = get_show_info(
            film_title, film_year, film_director,
            mc_scrape_df
            )

        # Initialize the movie's event description and runtime.
        movie_event_desc = None
        runtime = None
        if siskel_film_info_dict:

            runtime = int(siskel_film_info_dict.get("Runtime", "120"))

            movie_event_desc_header = \
                f'{film_year} | ' + \
                f'{str(runtime)} min.'
            
            if mc_film_info_dict:
                metascore = mc_film_info_dict.get('Metascore', None)
                if metascore:
                    movie_event_desc_header += f' | {metascore}'

            movie_event_desc = \
                movie_event_desc_header + \
                '\n\n' + \
                f'Director(s): {film_director}' + \
                '\n' + \
                f'{siskel_film_info_dict["Country"]}' + \
                '\n' + \
                f'{siskel_film_info_dict["Meta"]}' + \
                '\n\n' + \
                f'{siskel_film_info_dict["Description"]}'
            
        elif mc_film_info_dict:

            runtime = int(mc_film_info_dict['Runtime'])

            movie_event_desc = \
                f'{mc_film_info_dict["Year"]} | ' + \
                f'{mc_film_info_dict["Runtime"]} min. | ' + \
                f'{mc_film_info_dict.get("Metascore", 'N/A')}' + \
                '\n\n' + \
                f'Directed by: {mc_film_info_dict["Directors"]}' + \
                '\n' + \
                f'Written by: {mc_film_info_dict["Writers"]}' + \
                '\n\n' + \
                f'{mc_film_info_dict["Summary"]}'
            
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
            "colorId": 7,
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
        # print("Show added:",
        #         f'start={movie_start_str}', 
        #         f'end={movie_end_str}', 
        #         # f'\tlink={event.get('htmlLink')}',
        #         sep='\t')
        print(f"Event created: {film_title} at {movie_start_str} \t\t {event.get('htmlLink')}\n")



def schedule_siskel_shows_new_version():

    siskel_showtimes_df = None
    with open('data\pkl\siskel\siskel_showtimes.pkl', 'rb') as file:
        siskel_showtimes_df = pickle.load(file)

    siskel_info_df = None
    with open('data/pkl/siskel/siskel_show_info.pkl', 'rb') as file:
        siskel_info_df = pickle.load(file)

    mc_scrape_df = None
    with open('data/pkl/siskel/mc_scrape/siskel_show_info_mc_info.pkl', 'rb') as file:
        mc_scrape_df = pickle.load(file)

    creds = authenticate()
        
    try:
        service = build("calendar", "v3", credentials=creds)

        movie_radar_cal_id = '8b43bb1335dfcf5ae5bec565a51267c32d9a677cf134777510998bda8723c18c@group.calendar.google.com'

        # delete_all_events_from_cal(service, movie_radar_cal_id)

        delete_upcoming_events_from_cal(service, movie_radar_cal_id)

        already_scheduled_shows_df = get_showtime_df_from_cal(service, movie_radar_cal_id)

        # siskel_showtimes_df['Showtime'] = pd.to_datetime(siskel_showtimes_df['Showtime']).dt.tz_localize('UTC').dt.tz_convert('America/Chicago')

        new_shows_df = pd.merge(
            siskel_showtimes_df, already_scheduled_shows_df,
            how='left', on=['Title', 'Showtime'], indicator=True,
            ).query('_merge == "left_only"').drop(columns=['_merge'])
        
        insert_events_of_siskel_shows(
            new_shows_df, siskel_info_df, mc_scrape_df, service, movie_radar_cal_id
            )


    except HttpError as error:
        print("An error occurred:", error)
    

if __name__ == '__main__':



    schedule_siskel_shows_new_version()
