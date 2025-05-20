import datetime as dt

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import pickle

import pandas as pd

from utils import get_show_info

def construct_showtime_data(
        showtime_df: pd.DataFrame,
        show_info_theater_df: pd.DataFrame,
        show_info_mc_df: pd.DataFrame,
        # film_title: str,
        # film_year: str,
        # film_director: str,
        # showtime,
):
    # Initialize a list that will ultimately form the full-detail 
    # showtime dataset.
    scheduled_showtime_list = []

    for _ , row in showtime_df.iterrows():
        film_title = row['Title']
        film_year = row['Year']
        film_director = row['Director']
        showtime = row['Showtime'].to_pydatetime()
        # print(film_title, film_year, film_director, showtime, sep='\n')

        this_films_info_musicbox = get_show_info(
            film_title, film_year, film_director,
            show_info_theater_df
            )
        
        this_films_info_mc = get_show_info(
            film_title, film_year, film_director,
            show_info_mc_df
            )
        
        # if this_films_info_mc:
        #     print(film_title+film_year)
        #     print(this_films_info_mc["Summary"])

        # Initialize this film's event description and runtime.
        movie_event_desc = None
        runtime = None
        format = None

        metascore = None

        show_desc = None
        writers = None
        cast = None

        # 
        if this_films_info_musicbox:

            runtime = int(this_films_info_musicbox.get("Runtime", "120"))

            format = this_films_info_musicbox.get("Format", None)
            if pd.isna(format):
                format = None

            writers = this_films_info_musicbox.get("Writer", None)
            cast = this_films_info_musicbox.get("Cast", None)

            metascore = None
            if this_films_info_mc:
                metascore = this_films_info_mc.get('Metascore', None)

            if this_films_info_mc:
                if not show_desc:
                    show_desc = this_films_info_mc.get("Summary", None)

            event_desc_header_list = [
                film_year,
                f'{str(runtime)} min.',
                str(metascore),
                format
                ]
            
            event_desc_header = ' | '.join(
                [s for s in event_desc_header_list if s and pd.notna(s)]
                )

            writer_credit_str = f'Written by: {writers}' if writers else None
            cast_credit_str = f'Cast: {cast}' if cast else None
            
            event_desc_credit_list = [
                f'Director(s): {film_director}',
                writer_credit_str,
                cast_credit_str
            ]
            event_desc_credits = '\n'.join(
                [s for s in event_desc_credit_list if s]
                )  
            
            # event_desc_header = \
            #     f'{film_year} | ' + \
            #     f'{str(runtime)} min.'

            # if pd.notna(format):
            #     event_desc_header += f' | {format}'

            movie_event_desc = '\n\n'.join([
                event_desc_header,
                event_desc_credits
            ])
            
        elif this_films_info_mc:

            runtime = int(this_films_info_mc.get("Runtime", "120"))
            metascore = this_films_info_mc.get('Metascore', None)
            
            mc_film_year = this_films_info_mc.get("Year", None)
            show_desc = this_films_info_mc.get("Summary", None)

            # print("\nMETACRITIC INFO CONSULTED:\n", this_films_info_mc)
            # if show_desc:
            #     print("\nMETACRITIC FILM DESC:", film_title + film_year, show_desc, sep='\n', end='\n\n')

            mc_directors = this_films_info_mc.get("Directors", None)
            
            mc_writers = this_films_info_mc.get("Writers", None)
            writers = mc_writers

            event_desc_header_list = [mc_film_year,
                                      f'{str(runtime)} min.',
                                      metascore
                                      ]
            event_desc_header = ' | '.join([s for s in event_desc_header_list if s and pd.notna(s)])

            event_desc_credits = '\n'.join([
                f'Directed by: {mc_directors}',
                f'Written by: {mc_writers}'
            ])

            movie_event_desc = '\n\n'.join([
                event_desc_header,
                event_desc_credits,
                show_desc
                ])

            # f'{mc_film_year} | ' + \
            # f'{str(runtime)} min. | ' + \
            # f'{this_films_info_mc.get("Metascore", 'N/A')}' + \
            '\n\n' + \
            f'Directed by: {mc_directors}' + \
            '\n' + \
            f'Written by: {mc_writers}' + \
            '\n\n' + \
            f'{show_desc}'
            
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


        this_films_showtime_record = {
            "title": film_title,
            "year": film_year,
            "director": film_director,
            "runtime": runtime,
            "format": format,
            "metascore": metascore,
            "show_desc": show_desc,
            "writers": writers,
            "cast": cast
        }
        
        scheduled_showtime_list.append(this_films_showtime_record)

    fulldetail_show_df = pd.DataFrame(scheduled_showtime_list)

    return fulldetail_show_df


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

    fulldetail_show_df = construct_showtime_data(mb_showtimes_df, mb_info_df, mc_scrape_df)
    fulldetail_show_df.to_csv('data/csv/musicbox/test/fulldetail_show.csv')

    print(fulldetail_show_df)