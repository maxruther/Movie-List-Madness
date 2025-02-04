# Scraping More Review Data
## *Web-scraping to gather additional reviewers*

In this fourth phase of my project, I gather ratings from additional reviewers by creating various webscrapers. Comprising my subpackage *critic_ratings.scrapers*, these webscrapers retrieve the following:
- For **Metacritic**:
    - **The individual review scores that form the *Metascores* of a list of films**. Such reviews are given by various accredited publications.

- For **Letterboxd**:
    - **Ratings given by a user's friends.** Given a list of films' titles and release years. *Requires user's Letterboxd credentials.*

    - **A list of a user's watched films, as recorded in their Letterboxd "Diary."** As this scraper's yielded list includes such films' titles and release years, it is auxiliary to that preceding. *Only requires a Letterboxd username.*


## Drilling down on the *Metascore*

After completing this project's preceding phase, where I improved the integrity of the review score data, I conducted some light analysis. This analysis seemed to indicate that the aggregate review score from *Metacritic* was highly determinant of my enjoyment of a film. 

There were also indications that the aggregate review scores from *RottenTomatoes* and *IMDb* didn't add to the prediction as much as I hoped. These all being aggregations of review scores, they might've reflected more of the same information rather than any that might contrast them.

So to break down the *Metacritic* aggregate into facets that might contrastingly inform, I drilled down on this statistic by scraping its constituent review scores. These are given by accredited publications of film criticism, and for each film they tend to number between 10 and 60.

Once I succeeded in scraping all these publications' review scores for the watched films of my movie list, I conducted correlation analysis on them to determine how much each publication aligns with my own ratings.


## Details on how they work

For the respective tasks of navigating and parsing the web pages of these film review aggregators, my webscrapers utilize the Selenium and BeautifulSoup packages. They primarily focus on the sites *Metacritic* and *Letterboxd*. For both these applications, the program is comprised of two scrapers, one auxiliary and the other primary.

### LetterBoxd

The programs retrieving data from *Letterboxd* combine to generate, for a specified user, a table of their friends' ratings of the films from their *Diary*. To do so, their *Diary* is first scraped by an auxiliary method.

**Note**: A *Diary* on *Letterboxd* functions as a published log or journal of one's moviegoing. Rather than as a private record, it is conventionally used to signal one's moviegoing to interested friends.

#### Diary Scrape

To retrieve the watches from a user's *Letterboxd* diary, my scraper requires a string specifying the URL representation of their username. With that, it navigates a Selenium Chrome webdriver to their *Letterboxd* diary. 

Through this webdriver, the scraper retrieves these watched films' titles, release years, and also the links to their dedicated *Letterboxd* pages. These links can be used by the primary scraper, which retrieve the users' friends' ratings. 

Once the watches from every page of the diary have been scraped, the data is locally saved to file.

#### Friends' Ratings Scrape

In order to scrape a user's friends' ratings of their watches, the program has two requirements:
1) The films' *Letterboxd* page URLs, as retrieved by the preceding (auxiliary) scraper.
2) The log-in credentials of the user, specified in a local file.

Equipped with these, this process logs into the user's *Letterboxd* account, reads in the URLs of the watched films, and retrieves from those pages the ratings given by that user's friends. Once finished, this data is locally saved to file.

### Metacritic

Similar to my *Letterboxd* processes, mine for *Metacritic* start by gathering links to the site's webpages corresponding to a list of watched films. However, they constrast in how they identify those links: for *Metacritic*, the links are identified through search. (For *Letterboxd*, links were easily identified in the user's history, essentially, their *Diary*.)

Once such links have been provided by the auxiliary scraper, the primary one can retrieve all the individual review scores and snippets that form those films' *Metascores*. These reviewers are accredited publications of film criticism and more.

#### Link Scrape

The *Metacritic* link scraper first requires a table (DataFrame) of films' titles and release years. To search each table item, the title and year are concatenated and transformed into a URL string conducive to a *Metacritic* search request. That string forms the concluding segment of such a URL, which is then requested through a Selenium Chrome webdriver.

The webdriver then gathers the search results of the first page, evaluates those results' similarities to the searched item, then selects the best match. The link of this best match is logged as associated to the searched film.

In this way, the *Metacritic* pages that correspond to the listed films are iteratively retrieved. Both during this process and after, the retrieved data is written to file, in both an informal log and a more presentable *csv*.

For ~200 films, this process takes just over 20 minutes on my PC.

#### Critic Review Scrape

The scraping of the *Metascore* critical reviews can begin, once the links have been scraped as above. With those links, a Selenium Chrome webdriver is navigates to each film's "Critic Reviews" page, where only the reviews featured are from select publications.

The reviews are each represented in highly similar HTML elements, which typically show a review's score, date, author, and publication. Also commonly shown is a snippet from the written article that reflects the score. My scraper parses all this information precisely, using CSS selectors corresponding to each attribute. Ultimately, this information is used to form a table and save it locally to file.


## Future Work

I intend to revisit this area of my project to make the following enhancements:
    - Refactor the scrapers for *Metacritic* to clearly reflect that one is auxiliary and the other primary. Currently, they instead strike me as representing (misleadingly) two separate methods of comparable utility.

    - Revisit the scrapers for the *RogerEbert* site, now that I am more facile with Selenium and web-scraping, generally.

Though there's clearly more to this area of my project that I would like to improve with web-scraping, I have instead applied this skill to a new area: showtimes...

## Next up: Scraping Movie Showtimes (**IN-PROGRESS**)

In Chicago, some of the best movie theaters are independent ones. These tend not to appear on showtime aggregators like *Fandango*. For the next phase of my project, I (delicately) scrape showtimes from the webpages of independent theaters, then add those shows to Google Calendars as events.

