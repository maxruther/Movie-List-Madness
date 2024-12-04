from typing import List, Dict

import pymysql

from omdb_builder.omdb_loaders import download_omdb_data, unpickle_omdb_data


def load_omdb_data(method: str,
                   cursor: pymysql.cursors.Cursor = None,
                   raw: bool = False
                   ) -> List[List[Dict[str, str | int]]] | \
                       List[List[str | int | List[Dict[str, str]]]] | \
                       None:
    valid_methods = ['load from file', 'request through OMDB API']

    # Raise error if specified method of data retrieval isn't covered.
    if method not in valid_methods:
        print("ERROR: entry for 'method' parameter not valid. Please"
              "enter one of the following instead: ")
        for valid_method in valid_methods:
            print(valid_method)
        return

    else:
        # When loading/unpickling OMDB data from file.
        if method == 'load from file':
            if not raw:
                return unpickle_omdb_data()
            else:
                return unpickle_omdb_data(raw=True)

        # When requesting fresh OMDB data through their API.
        elif method == 'request through OMDB API':
            if not cursor:
                print("ERROR: load_omdb_data() needs a pymysql cursor"
                      "in order to get OMDB records via method 'request"
                      "from OMDB'")
            else:
                if not raw:
                    return download_omdb_data(cursor)[1]
                else:
                    return download_omdb_data(cursor)[0]
