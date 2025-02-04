# Movie List Ingestion - Quick Overview
## *Parsing and Loading my Movie List to MySQL*

The first phase of this project, handled by my **movielist_ingestion** package, parses my movie list and loads its data into a local MySQL database.

## My List

My movie list is a little idiosyncratic. It consists of many tables representing my various priorities in moviegoing. At the top, my "frontburner" and "critical backburner" are shown. The "frontburner" tracks my most immediate watchlist concerns as well as some of my most recent watches. 

<center><img src="Presentation/pics for quick overview/movielist - frontburner + backburner.png" width="60%"/> </center>
<br></br>

There is a lot of variety to my movie list's tables. Some represent recommends from friends or podcasts, while others are simply genre-specific. Some examples from both these categories are the *Holiday*, *Doc*, and *Friend Recommends* tables, pictured below:

<br></br>
<center><img src="Presentation/pics for quick overview/genre tables - holiday + docs.png" width="50%" height="20%"/> </center>
<br></br>
<center><img src="Presentation/pics for quick overview/movielist tables - friend recommends.png" width="50%" height="20%"/> </center>
<br></br>

## This ingestion program's aim and function

The variety of this list's tables is important to me, as is the freedom to create new tables whenever I like. These virtues are supported by both the python program that ingests the movie list's data as well as the MySQL database that then houses it. At the same time, this program and database introduce substantial improvements to that data's integrity and accessibility. Together, they identify and report anomalies, reconcile duplicate records, and facilitate easy querying, ultimately.

That ease of querying might best be demonstrated by a couple of the database's tables, "allwatched" and "allunwatched". These respectively consist of all watched and unwatched movie list items, as aggregated from all the various tables and listed uniquely. They are formed by pre-defined SQL procedures, which are called just after the completion of the movie list's parsing and loading.

<br></br>
<center><img src="Presentation/pics for quick overview/sql query - allunwatched.png" width="60%" height="20%"/> </center>
<br></br>
<center><img src="Presentation/pics for quick overview/sql query - allwatched.png" width="60%" height="20%"/> </center>
<br></br>

But of course, the movie list's original tables are reflected here in the database too. Like that of the "frontburner," which was shown in its initial Evernote form at the top of this document:

<br></br>
<center><img src="Presentation/pics for quick overview/sql query - frontburner_og.png" width="60%" height="20%"/> </center>
<br></br>

## Details on how it works

I start by exporting my movie list in Evernote to HTML format. To then build the database, I run my script  *build_movielist_db.py*, which includes a call to the method *evernote_to_mysql()*. This method handles the parsing and loading of that movie list HTML, the entire concern of this subproject.

### HTML-Parsing

Using BeautifulSoup, it identifies 'h2' HTML headers as table names. It identifies the tables themselves as 'en-table' elements. Because these headers and their corresponding table elements are unlinked formally in the file, it is important that they match in count and order.

As each table is identified by the program, its cells are parsed before the next is considered. The various data types of entries therein- strings, checkboxes, dates, and nulls- are all handled accordingly. These values are often adjusted to better fit the formatting of SQL insert statements, which ultimately marshall their loading. Once a complete row is formed of these values, it is prepended with an index named *MovieID*.

If multiple rows share film title and director, they are treated as duplicates. These mismatches are reconciled by overwriting the newer record to reflect the older. This reconciliation helps to remedy instances of duplicate *MovieID* values.

### Loading to MySQL

The above process of HTML-parsing yields something akin to a 3D-list, where each 2D-list within it represents a table from the original file. From this 3D-list comprised of the movie list data, the database's tables are built from scratch (or re-built, if they already exist.) 

This involves dropping all tables from the MySQL movie list database, then recreating and populating them. The latter task is performed by automatically drafting 'CREATE TABLE' and 'INSERT' SQL statements from the ingested data, which contains the Evernote tables' names and attribute headers in addition to the records. In this way, tables are constructed in the MySQL database that match those of the Evernote file.

Before this process concludes, a few more MySQL tables are formed from those sourced in the Evernote HTML. These are the "allwatched", "allunwatched", and "allmovies" tables, which are each created by the invocation of a pre-defined SQL procedure. These respectively list all watched movies, all unwatched movies, and all movies. The table of all watched movies might be especially important, as its contents are later used to train predictors of ratings.

## Next up: Enriching the Film Data

In the next phase of my project, I enrich my film data by incorporating that of an open source database: *The Open Movie Database (OMDb)*.