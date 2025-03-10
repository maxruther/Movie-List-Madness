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

        movies_missing_runtime = []

        siskel_showtimes_dict = None
        with open('data/showtimes/siskel_films_showtimes_dict.pkl', 'rb') as file:
            siskel_showtimes_dict = pickle.load(file)

        siskel_film_details_dict = None
        with open('data/showtimes/siskel_films_details_dict.pkl', 'rb') as file:
            siskel_film_details_dict = pickle.load(file)

        mc_scrape_df = None
        with open('data/scraped/showtime_mc_detail_scrape.pkl', 'rb') as file:
            mc_scrape_df = pickle.load(file)

        missing_from_mc_scrape = []

        for movie_title in siskel_showtimes_dict:

            # Initialize the movie's event description and runtime.
            movie_event_desc = None
            runtime = None

            # If the movie is in the Metacritic-scraped film details, then 
            # use those to create an in-depth event description.
            if movie_title in mc_scrape_df['Title'].values:
                film_detail_record = mc_scrape_df[mc_scrape_df['Title'] == movie_title]
                film_detail_dict = film_detail_record.to_dict(orient='records')[0]

                runtime = int(film_detail_dict['Runtime'])

                movie_event_desc = \
                    f'{film_detail_dict["Year"]} | ' + \
                    f'{film_detail_dict["Runtime"]} min. | ' + \
                    f'{film_detail_dict.get("Metascore", 'N/A')}' + \
                    '\n\n' + \
                    f'Directed by: {film_detail_dict["Directors"]}' + \
                    '\n' + \
                    f'Written by: {film_detail_dict["Writers"]}' + \
                    '\n\n' + \
                    f'{film_detail_dict["Summary"]}'
                
                # print(movie_title, '\n')
                # print(movie_event_desc)
                # print('\n', '-'*80, '\n', sep='')

            # If the movie wasn't MC-scraped for, then use a generic
            # event description.
            else:
                movie_event_desc = 'No details available.'

                # If the siskel scrape didn't get the runtime for the movie,
                # then set that to a default of 120 minutes.
                if 'Runtime' not in siskel_film_details_dict[movie_title]:
                    print(f'RUNTIME MISSING FOR FILM "{movie_title}"')
                    movies_missing_runtime.append(movie_title)
                    runtime = 120
                    movie_event_desc += '\n\nRuntime missing - Set to 120-minute default.'

                # Otherwise, use the runtime scraped from the Siskel page.
                else:
                    runtime = siskel_film_details_dict[movie_title]['Runtime']
                    print(f'\nFilm: {movie_title}\t\tRuntime: {runtime} minutes')


            # Slate the movie for each of its showtimes.
            for showtime in siskel_showtimes_dict[movie_title]:

                # Calculate the show's end time from its start time and runtime.
                runtime_delta = dt.timedelta(minutes=runtime)
                movie_start_str = showtime.strftime('%Y-%m-%dT%H:%M:%S')
                movie_end = showtime + runtime_delta
                movie_end_str = movie_end.strftime('%Y-%m-%dT%H:%M:%S')
                # print(movie_title, runtime, movie_start_str, movie_end_str, sep='\t')

                # Construct the event object for insertion into the calendar.
                event = {
                    "summary": movie_title,
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


    # siskel_showtimes_dict = None
    # with open('data/showtimes/siskel_films_showtimes_dict.pkl', 'rb') as file:
    #     siskel_showtimes_dict = pickle.load(file)

    # siskel_film_details_dict = None
    # with open('data/showtimes/siskel_films_details_dict.pkl', 'rb') as file:
    #     siskel_film_details_dict = pickle.load(file)


    # mc_scrape_df = None
    # with open('data/scraped/showtime_mc_detail_scrape.pkl', 'rb') as file:
    #     mc_scrape_df = pickle.load(file)

    # missing_from_mc_scrape = []

    # for movie_title in siskel_showtimes_dict:

    #     if movie_title not in mc_scrape_df['Title'].values:
    #         missing_from_mc_scrape.append(movie_title)
        
    #     else:
    #         film_detail_record = mc_scrape_df[mc_scrape_df['Title'] == movie_title]
    #         film_detail_dict = film_detail_record.to_dict(orient='records')[0]

    #         movie_event_desc = \
    #             f'{film_detail_dict["Year"]} | ' + \
    #             f'{film_detail_dict["Runtime"]} min. | ' + \
    #             f'{film_detail_dict.get("Metascore", 'N/A')}' + \
    #             '\n' + \
    #             f'Directed by: {film_detail_dict["Directors"]}\n' + \
    #             f'Written by: {film_detail_dict["Writers"]}\n' + \
    #             '\n' + \
    #             f'{film_detail_dict["Summary"]}'
    #         print(movie_title, '\n')
    #         print(movie_event_desc)
    #         print('\n', '-'*80, '\n', sep='')

    # print(f'Missing from Metacritic scrape: {missing_from_mc_scrape}')

    # print(mc_scrape_df.keys())

    # print(mc_scrape_df[mc_scrape_df['Title'] == 'INCENDIES']['Year'])