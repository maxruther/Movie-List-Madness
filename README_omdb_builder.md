# Movie Data Enriching - Quick Overview
## *Building out my movie data with that of external source,* OMDb

In this second phase of my project, I enrich my movie list database by incorporating that of *The Open Movie Database (OMDb)*. The processes of this second phase of data ingestion comprise the **omdb_builder** package.

## My Database versus *OMDb*

This open source database, *OMDb*, affords much richer film data than my own movie list offers. Without any broadening, my own data only offers the following film information: title, director, production year, and US release date:

<br></br>
<center><img src="Presentation/pics for quick overview/sql query - frontburner_og.png" width="80%" height="20%"/> </center>
<br></br>

The *OMDb* data goes far beyond this, containing attributes like cast, runtime, genres, and review scores from a few major aggregators of film criticism. To illustrate, an image of their record for the film *Nickel Boys (2024)*:

<br></br>
<center><img src="Presentation/pics for quick overview/omdb - nickel boys.png" width="80%" height="20%"/> </center>
<br></br>

I felt that adding this external data to my database would greatly enrich it, not least because it might enhance its capability for predicting my ratings.


## Details on how it works

I used the OMDb API in a Python program to retrieve and load their film records that corresponded to my watches. I found parsing this data to be more complex than what was necessary for my own watch data (in this project's preceding phase.) It faced me with a couple new challenges, among others:
    - handling the OMDb responses' nested dictionaries
    - pivoting wider its genre data, creating many binary genre attributes from a single categorical one


### Retrieving *OMDb* data

Rather than attempt to retrieve *all* of the data available on *OMDb*, my program only seeks the records relevant to my local movie-list database. So it starts by getting a list of all those movies, by querying its *allMovies* table. The contents of this query, namely the films' titles and release years, are used as specifications in iterative requests to *OMDb* using its API. Any failed requests are reported to the user.

The responses then received from OMDb are stored to file, which, as JSON files, here resemble extensive Python dictionaries. To simplify things, my process also stores shorter versions of these *OMDb* records, selecting just eight of their attributes instead. The storage of this data to file allows for the skipping of the requesting process, should the user prefer that in future reconstructions of the database.

### Testing what's retrieved

Once the retrieval of this *OMDb* data is complete, it is tested for discrepancies against the data existing in the MySQL database, in its *allMovies* table. The process-generated key *MovieID* is partly enforced here, as film records sharing that key are tested as also sharing title and release year.

### Parsing further then loading to MySQL

With testing done, the *OMDb* data is ready for the final stage of this process: loading into my local MySQL database. Therein, this *OMDb* data is eventually loaded into a few dedicated tables: 
- *omdb*: simply contains the feature-selected OMDb records.
- *genres*: Indicates each film's associated genres, which are each represented by a binary attribute.
- *critic_ratings*: Contains each film's review scores from a few major aggregators of film criticism (*Rotten Tomatoes*, *IMDb*, and *Metacritic*. I expand this table to also include *RogerEbert* scores, in this project's next phase.)

Each table has dedicated methods for parsing the *OMDB* data further and then loading it. Such parsing variously consists of cleaning strings; handling null values; type-transforming numeric data; and parsing review scores from their nested dictionary. The loading consists of programatically drafting and executing SQL 'INSERT' statements.

## Next up: Improving the review score data

In the next phase of my project, I hone in on this *OMDb* data's aggregate review scores. Identifying many missing values, I code processes to report and remap them. I also add a process that joins in scores from another external source of reviews.
