# Movie List Ingestion - Subproject #1
## *Parsing and Loading my Movie List to MySQL*

In this first phase of my movie project, I parse an HTML version of my movie list and load the data into a local MySQL database. Once loaded, that data then populates three newly created MySQL tables, through predefined MySQL procedures.

<!-- <br></br> -->
<center><img src="../Presentation/pics for quick overview/1 - intro - before after.png" width="80%" height="20%"/> </center>
<br></br>

From that data, the process then creates three new tables, through predefined MySQL procedures. Two of these new tables separate the movies based on whether they've been watched or not. This separation might be a convenient feature of my database, given that in the original HTML movie list, these records instead tend to be intermingled messily.

<!-- <br></br> -->
<center><img src="../Presentation/pics for quick overview/1 - movies sorted watched unwatched.png" width="80%" height="20%"/> </center>
<br></br>


## Details

For more details on this process of parsing and loading my Evernote movie list to a local MySQL database, please read on. I have organized break-downs into the following sections, in this same order:

- [My Movie List](#my-movie-list): An overview of my movie list document, which might serve as the core data of this sprawling project.
- [Motivations](#motivations): My motivations, goals, and achievement thereof for this first subproject.
- [Process Details](#process-details): A more detailed overview of how this process functions.

### My Movie List

There are some quirks to [my movie list:](../movie_lists/Movies.html)
- **It resembles a to-do list,** where completed task items are retained (rather than deleted from the document.) So for my moviegoing, it functions as both a log of viewings and a watchlist/queue.

- **I maintain the list in *Evernote***, a productivity app. To prepare it for my program's processing, it is necessary to first export the list to HTML format.

- **Over a dozen various tables** comprise my movie list, representing a range of categories. These categories are often mutually non-exclusive, so much so that they often share **duplicate records.** (e.g. a film can appear in both the "Drama" table and the "Faves" table.)

- The tables' categories tend to relate one of the following subjects:
    - genre
    - recommendation source (e.g. friends, critics, podcasts...)
    - priority of the watch (e.g. currently in theaters, available to stream, classic films that've long been on the backburner...)

One of my watch priority-related tables is illustrated below, the "frontburner" table. There, I enter my most immediate watchlist concerns, as well as some of my most recent watches.

<center><img src="../Presentation/pics for quick overview/movielist - frontburner + backburner.png" width="60%"/> </center>
<br></br>

There is a lot of variety to my movie list's tables. Some represent recommends from friends or podcasts, while others are simply genre-specific. 

Below are some examples of tables relating to genre or recommendations, those of *Holiday*, *Doc*, and *Friend Recommends*:

<br></br>
<center><img src="../Presentation/pics for quick overview/genre tables - holiday + docs.png" width="50%" height="20%"/> </center>
<br></br>
<center><img src="../Presentation/pics for quick overview/movielist tables - friend recommends.png" width="50%" height="20%"/> </center>
<br></br>

### Motivations
#### *This program's aim and function*

The variety of this list's tables is important to me, as is the freedom to create new tables whenever I like. These virtues are supported by both the python program that ingests the movie list's data as well as the MySQL database that then houses it. At the same time, this program and database introduce substantial improvements to that data's integrity and accessibility. Together, they identify and report anomalies, reconcile duplicate records, and facilitate easy querying, ultimately.

That ease of querying might best be demonstrated by a couple of the database's tables, "allwatched" and "allunwatched". These respectively consist of all watched and unwatched movie list items, as aggregated from all the various tables and listed uniquely. They are formed by pre-defined SQL procedures, which are called just after the completion of the movie list's parsing and loading.

<br></br>
<center><img src="../Presentation/pics for quick overview/sql query - allunwatched.png" width="60%" height="20%"/> </center>
<br></br>
<center><img src="../Presentation/pics for quick overview/sql query - allwatched.png" width="60%" height="20%"/> </center>
<br></br>

But of course, the movie list's original tables are reflected here in the database too. Like that of the "frontburner," which was shown in its initial Evernote form at the top of this document:

<br></br>
<center><img src="../Presentation/pics for quick overview/sql query - frontburner_og.png" width="60%" height="20%"/> </center>
<br></br>

### Process Details

I start by exporting my movie list in Evernote to HTML format. To then build the database, I run my script  *build_movielist_db.py*, which includes a call to the method *evernote_to_mysql()*. This method handles the parsing and loading of that movie list HTML, the entire concern of this subproject.

#### HTML-Parsing

Using BeautifulSoup, it identifies 'h2' HTML headers as table names. It identifies the tables themselves as 'en-table' elements. Because these headers and their corresponding table elements are unlinked formally in the file, it is important that they match in count and order.

As each table is identified by the program, its cells are parsed before the next is considered. The various data types of entries therein- strings, checkboxes, dates, and nulls- are all handled accordingly. These values are often adjusted to better fit the formatting of SQL insert statements, which ultimately marshall their loading. Once a complete row is formed of these values, it is prepended with an index named *MovieID*.

If multiple rows share film title and director, they are treated as duplicates. These mismatches are reconciled by overwriting the newer record to reflect the older. This reconciliation helps to remedy instances of duplicate *MovieID* values.

#### Loading to MySQL

The above process of HTML-parsing yields something akin to a 3D-list, where each 2D-list within it represents a table from the original file. From this 3D-list comprised of the movie list data, the database's tables are built from scratch (or re-built, if they already exist.) 

This involves dropping all tables from the MySQL movie list database, then recreating and populating them. The latter task is performed by automatically drafting 'CREATE TABLE' and 'INSERT' SQL statements from the ingested data, which contains the Evernote tables' names and attribute headers in addition to the records. In this way, tables are constructed in the MySQL database that match those of the Evernote file.

Before this process concludes, a few more MySQL tables are formed from those sourced in the Evernote HTML. These are the "allwatched", "allunwatched", and "allmovies" tables, which are each created by the invocation of a pre-defined SQL procedure. These respectively list all watched movies, all unwatched movies, and all movies. The table of all watched movies might be especially important, as its contents are later used to train predictors of ratings.

<br></br>

## Next up: [Enriching the Film Data](../omdb_builder/README_omdb_builder.md)

In the next phase of my project, I enrich my film data by incorporating that of an open source database: *The Open Movie Database (OMDb)*.