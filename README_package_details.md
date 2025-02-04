# Custom Package Details

Please read on for more details on each of the custom packages.

## 1. **movielist_ingestion**

Initially, the focus of this project was to create my own MySQL database, to house my watchlist's data and afford easy querying thereof. This mainly involved parsing an HTML of my watchlist, dynamically writing SQL statements to create its various tables, accordingly inserting records therein, and preparing and triggering SQL procedures that draw from these initial tables. These tasks and more comprise my **movielist_ingestion** package.


## 2. **omdb_builder**

Next, I sought to enrich this data by incorporating that of *The Open Movie Database (OMDb)*. This open source database afforded film records that were much more complete than my own. I used their API to retrieve and load such records that corresponded to my watches, so broadening my data. The ingestion of this new data required slightly more complex parsing, to handle its nested dictionaries and to pivot genre data wide, to transform its type from categorical to binary. The processes of this second phase of data ingestion, to incorporate OMDb data, comprise the **omdb_builder** package.

## 3. **critic_ratings.RatingsTableMender**

The addition of OMDb data provided my project's first critical review scores, to which I then shifted its focus. Some preliminary analysis revealed that these review score attributes were missing values, often erroneously: online searches would often demonstrate instead that such review scores' existed. To mitigate such scarcity in my already small sample of film watches, I coded several functionalities in **RatingsTableMender**, the sub-package of **critic_ratings**:
1) Report the titles of each reviewer's missing scores, as value-less dictionary literals conducive to manual mapping.
2) Apply these mappings to the missing scores, once they're manually completed.
3) Add a new reviewer's film ratings, given a list of them that also includes the films' titles and release years.

This way, the Rotten Tomatoes, IMDb, and Metacritic review scores were better filled out. Also review scores from RogerEbert.com were added in (which I had then recorded manually, regrettably.) A decision tree trained off these scores and my own ratings revealed that those of Metacritic predict my enjoyment most strongly. This motivated the next and latest phase of my project...

## 4. **critic_ratings.scrapers**

To drill down on the correlation between my ratings and the critical aggregates from Metacritic, I web-scraped the individual critic reviews that form them. This process as well as others for the sites Letterboxd and RogerEbert comprise **scrapers**, another of my subpackages of **critic_ratings**. The Letterboxd scrapers combine to retrieve a user's friends' ratings of the films they've watched, given that user's log-in credentials.
