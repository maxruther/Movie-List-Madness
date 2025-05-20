import os.path
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from json.decoder import JSONDecodeError

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from datetime import datetime, date, timedelta

from schedule_musicbox_shows import insert_events_of_mb_shows, delete_all_events_from_cal
from utils import authenticate
from testing_utils import get_first_n_days_of_showtime_df

import pandas as pd


def delete_upcoming_events_from_cal(
        google_cal_service,
        cal_id: str,
        ) -> None:
    
    page_token = None
    while True:
        events_result = google_cal_service.events().list(calendarId=cal_id, pageToken=page_token).execute()
        # for event in list(events_result['items'])[:5]:
        for event in events_result['items']:
            event_id = event['id']
            event_summary = event['summary']
            event_start = event['start']['dateTime']
            event_start_dttime = datetime.fromisoformat(event_start)
            event_start_date = event_start_dttime.date()

            todays_date = date.today()

            # print(f"{event_summary}: {event_start_date}")

            # print(f"Event start date: {event_start_date}",
                #   f"Today's Date: {todays_date}")


            if event_start_date < todays_date:
                # print("EVENT DATE IS BEFORE TODAY\n")
                continue
            else:
                # print("EVENT DATE IS TODAY OR AFTER\n")
                google_cal_service.events().delete(calendarId=cal_id, eventId=event_id).execute()
                print(f'DELETED UPCOMING EVENT: {event['summary']} AT {event['start']['dateTime']}')

            # print(event_id, event_summary, event_start)
            # print(type(event_start))
        
        page_token = events_result.get('nextPageToken')
        if not page_token:
            break

    return


if __name__ == '__main__':

    test_str = ['1992', None, 'Barbie', None, 'buttfuck']
    reformatted_str = ' | '.join([s for s in test_str if s])
    print(reformatted_str)

    # creds = authenticate()

    # test_cal_id = '806c0e2aac6fb8ce5f7fa446b3f2951b58c055e16a72f3c4e08711b4d813a0bc@group.calendar.google.com'

    # try:
    #     google_cal_service = build("calendar", "v3", credentials=creds)

    #     delete_all_events_from_cal(google_cal_service, test_cal_id)

    #     # delete_coming_events_from_cal(google_cal_service, test_cal_id)

    #     # LOAD FILM INFO DATA
    #     mb_info_df = None
    #     with open('data/pkl/musicbox/musicbox_show_info.pkl', 'rb') as file:
    #         mb_info_df = pickle.load(file)

    #     mc_scrape_df = None
    #     with open('data/pkl/musicbox/mc_scrape/musicbox_show_info_mc_info.pkl', 'rb') as file:
    #         mc_scrape_df = pickle.load(file)

    #     # LOAD SHOWTIMES DATA
    #     mb_showtimes_df = None
    #     with open('data/pkl/musicbox/musicbox_showtimes.pkl', 'rb') as file:
    #         mb_showtimes_df = pickle.load(file)

    #     # CREATE TEST DATA OF SHOWTIMES
    #     first_day_of_showtimes_df = get_first_n_days_of_showtime_df(mb_showtimes_df, 1)
    #     first_3_days_of_showtimes_df = get_first_n_days_of_showtime_df(mb_showtimes_df, 3)

    #     # # CREATE SHOWTIME TEST DATA CENTERED ON TODAY'S DATE
    #     # today = date.today()
    #     # n_days_of_shows_to_slate = timedelta(days=2)
    #     # test_show_df = mb_showtimes_df[mb_showtimes_df['Showtime_Date'] <= today + n_days_of_shows_to_slate]

    #     # shows__up_to_today_df = mb_showtimes_df[mb_showtimes_df['Showtime_Date'] <= today]
    #     # shows__up_to_2_days_ltr_df = mb_showtimes_df[mb_showtimes_df['Showtime_Date'] <= today + n_days_of_shows_to_slate]


    #     insert_events_of_mb_shows(first_day_of_showtimes_df, mb_info_df, mc_scrape_df, google_cal_service, test_cal_id)

    #     print(pd.merge(first_3_days_of_showtimes_df, first_day_of_showtimes_df, how='left', on=['Title', 'Showtime'], indicator=True).query('_merge == "left_only"').drop(columns=['_merge']))
        
    # except HttpError as error:
    #         print("An error occurred:", error)
        
