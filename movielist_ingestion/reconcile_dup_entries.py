
def reconcile_dup_entries(new_record: dict[str : str | int],
                        old_record: dict[str : str | int],
                        reconcile: bool = True,
                        verbose: bool = False,
                        ) -> dict[str : str | int]:
    
    # Discrepancy dictionary, to store the warnings of how the two entries 
    # differ.
    discr_dict = {
        'Unshared Attribute': [],
        'Value Change': [],
        }

    discr_count = 0
    discr_found = False

    # print(' ', old_entry, new_entry, sep='\n', end='\n\n')

    for attr in new_record:
        if attr not in old_record:
            discr_found = True
            discr_count += 1

            discr_str = f"'{attr}' attribute not in OLD record. \n" +\
                f"\tIn NEW record:  {attr} = {new_record[attr]}"
            
            discr_dict['Unshared Attribute'].append(discr_str)
        else:
            if new_record[attr] != old_record[attr]:
                # if attr == 'Movie_ID':
                #     continue

                discr_found = True
                discr_count += 1

                discr_str = f'For attribute {attr}, the values differ: \n' + \
                    f'\tIn NEW record:\t{attr} = {new_record[attr]} \n' + \
                    f'\tIn OLD Record:\t{attr} = {old_record[attr]}'
                discr_dict['Value Change'].append(discr_str)

    for attr in old_record:
        if attr not in new_record:
            discr_found = True
            discr_count += 1

            discr_str = f"'{attr}' attribute not in NEW record. \n" +\
                f"\tIn OLD record:  {attr} = {old_record[attr]}"
            
            discr_dict['Unshared Attribute'].append(discr_str)


    if discr_found:
        longer_dashline = '-' * 100
        shorter_dashline = '-' * 50
        discr_warning_str = f"\nWARNING: Records of film " + \
            f"{new_record['Title']} by " + \
            f"{new_record['Director']} differ.\n" + \
            f"Discrepancy count = {discr_count}\n"

        if verbose:
            print(longer_dashline,
                discr_warning_str,
                new_record,
                old_record,
                sep='\n', end='\n\n')
            
            for discr_type in discr_dict:
                if discr_dict[discr_type]:
                    print(shorter_dashline,
                        discr_type.upper() + ':',
                        sep='\n\n')
                    for warning in discr_dict[discr_type]:
                        print(warning, '\n')
            print(longer_dashline + '\n')

    if reconcile:
        result_entry = new_record.copy()
        
        for attr in new_record:
            if attr in old_record:
                result_entry[attr] = old_record[attr]
        
        if verbose:
            print('ADJUSTED RECORD:',
                    result_entry,
                    '\nFrom these records:',
                    f'OLD: {old_record}',
                    f'NEW: {new_record}',
                    sep='\n')
        
        return result_entry



if __name__ == '__main__':
    new_header = ['Movie_ID', 'Title', 'Director', 'Watched', 'Rating',
                 'Year', 'Release_Date', 'Watched_in_theater',
                   'Date_watched']
    new_data = [273, "'Pokemon 2000'", "'Yuyama / Haigney'", 1, 'NULL', "'2000'", "'7/21/00'", 0, "'9/1/23'"]

    old_header = ['Movie_ID', 'Title', 'Director', 'Watched', 'Recommending', 'Rating', 'Year', 'Release_Date', 'Watched_in_theater', 'Date_watched']
    old_data = [213, "'Pokemon 2000'", "'Yuyama / Haigney'", 1, 'NULL', 'NULL', "'2000'", "'7/21/00'", 0, "'9/1/23'"]

    new_header = ['Movie_ID', 'Title', 'Director', 'Watched', 'Friend_recommending', 'Rating', 'Year', 'Release_Date', 'Watched_in_theater', 'Date_watched']
    new_data = [74, "'Evil Does Not Exist'", "'Hamaguchi'", 0, "'NYT'", 'NULL', "'2023'", "'5/3/24'", 0, 'NULL']

    old_header = ['Movie_ID', 'Title', 'Director', 'Watched', 'Recommending', 'Rating', 'Year', 'Release_Date', 'Watched_in_theater', 'Date_watched']
    old_data = [6, "'Evil Does Not Exist'", "'Hamaguchi'", 1, "'NYT'", "'PRETTY AWESOME'", "'2023'", "'5/3/24'", 1, "'12/21/24'"]

    new_record = dict(zip(new_header, new_data))
    old_record = dict(zip(old_header, old_data))


    reconciled_new_record = reconcile_dup_entries(new_record, old_record, 
                                             reconcile=True)
    
    print(f'\n{old_record=}', f'{new_record=}', f'\n{reconciled_new_record=}\n',
          sep='\n')