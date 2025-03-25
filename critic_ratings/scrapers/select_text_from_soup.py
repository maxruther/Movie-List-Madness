from bs4 import BeautifulSoup

def select_text_from_soup(element_name: str, 
                        the_soup: BeautifulSoup,
                        css_select_str: str,
                        mute=True,
                        ) -> str:
        """From a BeautifulSoup object, get the stripped text of
        the first element of a possibly numerous CSS-selection,
        given a name for the desired element; the
        BeautifulSoup object of the critic review; and the
        string to be submitted to the Soup's select() method.

        I use this function instead of BeautifulSoup.select_one() 
        because I want to be alerted when there are multiple 
        elements found, and to write in my own exceptions here."""

        # Select all elements from the Soup that fit the 
        # specifications.
        element_selection = the_soup.select(css_select_str)

        # If it isn't exactly one element that has been selected, 
        # print feedback to
        # indicate this unmet expectation.
        selection_count = len(element_selection)
        if selection_count != 1:
            if selection_count == 0:
                if not mute:
                     print("\n",
                    f"No {element_name} elements found.\n")
                data_element = ''
                return data_element
            else:
                if not mute:
                    print("\n",
                        f"There were {selection_count} elements of",
                        f"{element_name} found:\n")
                    for i in element_selection:
                        print(i, '\n\n')
                    print()

        # Take the text of the first element found, strip it, then 
        # return it.
        data_element = element_selection[0].text.strip()

        return data_element
