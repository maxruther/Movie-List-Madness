import re


def tech_summary_list_to_dict(tech_summary_list: list[str],
                                ) -> dict[str: int | str]:
    """For the Music Box scrape, this function takes a list of strings 
    containing a film's technical details and returns a dictionary 
    thereof. Such a dictionary is more suitable for the scheduling 
    methods that operate on this data."""

    tech_details = {}

    year_pattern = r'^(\d{4})$'
    runtime_pattern = r'^(\d*) mins?$'
    format_pattern = r'(^DCP$|^\d\.\dmm$|^\d{1,3}mm$)'

    for tech_detail in tech_summary_list:

        year_match = re.search(year_pattern, tech_detail)
        runtime_match = re.search(runtime_pattern, tech_detail)
        format_match = re.search(format_pattern, tech_detail)

        if year_match:
            tech_details['Year'] = year_match.group(1)
            # print(tech_details['Year'])
            # print(type(tech_details['Year']))
        elif runtime_match:
            tech_details['Runtime'] = int(runtime_match.group(1))
            # print(tech_details['Runtime'])
            # print(type(tech_details['Runtime']))
        elif format_match:
            tech_details['Format'] = format_match.group(1)
            # print(tech_details['Format'])
            # print(type(tech_details['Format']))

    return tech_details


def parse_show_name(show_name: str,
                        ) -> str:
        """Parse a Siskel show's title into those of the series and film,
        which sometimes comprise it.
        
        An auxiliary method of the siskel_scrape."""

        film_title = None
        series_prepends = None


        if ': ' in show_name:
            parsed_show_name = show_name.split(': ')

            # In the event that the film title contains a single
            # colon, detect and combine its erroneously split 
            # segments.
            if len(parsed_show_name) >= 2:
                potential_title_segment = parsed_show_name[-2]

                some_valid_series_names = ['OFF CENTER', 
                                        'ARTHUR ERICKSON',
                                        'ADFF',
                                        ]

                if potential_title_segment not in some_valid_series_names and \
                not any(char.islower() for char in potential_title_segment):
                    film_title = ': '.join(parsed_show_name[-2:])
                    series_prepends = parsed_show_name[:-2]
                else:
                    film_title = parsed_show_name[-1]
                    series_prepends = parsed_show_name[:-1]
        else:
            film_title = show_name
            series_prepends = None

        return film_title, series_prepends