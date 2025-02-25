# **Max's Movie Madness** - A Database Project
## *HTML-parsing personal movie journals, review websites, and more to build a MySQL database primed for ratings prediction.*

<br></br>
## Overview

This is a multi-faceted personal project that centers on personal moviegoing. It started with loading my [movie list](/movie_lists/Movies.html) to a local MySQL database, but sprawled out from there to take in data from various sources, especially film review scores.

My skills that this project may have exercised most are those in **ETL, HTML-scraping, and database management.**

If you would like more details on the course of this project and how its subprojects connect, please see [this section](#projects-course).


<!--
To create a database primed to predict my own ratings, I here embarked on a series of subprojects to build and enrich to such a one. These subprojects, which number at four and counting, mark various stages of the effort and have been organized into separate custom Python packages.

So organized, the course of this project can be chronologically traced through the below list of packages, which each contain dedicated *README_\*.md* files:
-->



<br></br>
## **The Subprojects (*Custom_Packages*)**

This project's course as I've just described it can be traced through the below list of packages, which each contain a dedicated *README_\*.md* file.



### 1. [**Movie List Ingestion**](/movielist_ingestion/README.md) ([*movielist_ingestion*](/movielist_ingestion/)): 
**HTML-parsing my movie list and loading that data into a local MySQL database.**
<br></br>

### 2. [**Enriching the Movie Data**](/omdb_builder/README.md) ([*omdb_builder*](/omdb_builder/)):
**Retrieving and loading in records from *The Open Movie Database (OMDb)*, to broaden my database.**
<br></br>

### 3. [**Improving the Review Score Data**](/critic_ratings/RatingsTableMender/README.md) ([*critic_ratings.RatingsTableMender*](/critic_ratings/RatingsTableMender/)):
**Programmatically reporting and remapping values that might be missing erroneously,** from the review scores featured in the *OMDb* data. **Also, joining in an additional reviewer, from file.**
<br></br>

### 4. [**Scraping to Add Reviewers**](/critic_ratings//scrapers/README.md) ([*critic_ratings.scrapers*](/critic_ratings/scrapers/)): 
**From various websites, scraping the following:**
- ***Metacritic***:
    - **Critical Review scores** - Films' individual reviews from various critical publications that are aggregated to form its "Metascore".
    - **Film Details** - Films' technical details, like release year, runtime, directors, writers, the date of its US theatrical release, and a descriptive summary.

- ***LetterBoxd***: 
    - ***LB* Diary Watches** - A specified user's moviegoing *Diary* for its films' titles, years, and the relative paths to their dedicated pages on *LB*.
    - **Critics & Friends' Ratings** - A specified users' friends' ratings of their own watched films.
<br></br>
    
<!-- - ***RogerEbert* (IN-PROGRESS)**: These scrapers are still in-progress, as they get blocked after only ~30 ratings scraped.
    - **Recent Ratings** - Scrape some of this site's most recent ratings.
    - **Ratings of Specified Films** - Scrape a film's rating, given its title and release year. -->

### 5. [**Scraping and Scheduling Showtimes**](/its_showtimes/README_its_showtimes.md) ([its_showtimes](/its_showtimes/))
**Scraping showtimes from the pages of Chicago's independent movie theaters, then scheduling them in Google Calendars.** So far covers the Music Box and the Siskel.

<!-- Web-scrape  individual reviews from various critical publications which are aggregated to form a film's "Metascore" on *Metacritic*. With these, I am able to analyze correlations between my ratings and those of prominent publications. This package also includes scrapers that I've built for the sites *Letterboxd* and *RogerEbert*. -->

<br></br>
## [**Analyses**](/Analysis/Jupyter%20HTMLs/)

I took my movie data for a spin with some analysis and modelling, once I was satisfied with the quality and integrity of my movie database. These analyses are presentably featured in the [**Analysis (Jupyter NBs)**](/Analysis/) directory, in both [*ipynb*](/Analysis/) and [*html*](/Analysis/Jupyter%20HTMLs/) files. These documents, which were deliberately written and organized with an interested reader in mind, might help to explain my project's structure and motivations:

1. [**Fixing the CR Table**](/Analysis/Fixing%20the%20CR%20Table.ipynb) - This first notebook isn't an analysis, but instead walks through the processes of my third subproject. That subproject involved making improvements to the review score data that was retrieved from *OMDb*, in the subproject preceding it.

2. [**Predicting My Ratings - First DT**](/Analysis/Predicting%20My%20Ratings%20-%20First%20DT.ipynb) - With the review score data now mended, thereon I train a first decision tree model to predict my own ratings.

3. [**Incorporating Genre - Second DT**](/Analysis/Incorporating%20Genre%20-%20Second%20DT.ipynb) - In an attempt to refine my decision tree model, I incorporate the films' genre data, which was retrieved and parsed from the *OMDb.*

4. [**Scraped Metacritic CR's (*IN-PROGRESS*)**](/Analysis/Scraped%20Metacritic%20CR's.ipynb) - After scraping all the individual critical reviews that make up my watched films' *Metacritic* aggregate scores (a.k.a. "*Metascores*") I perform a cursory analysis. Towards the end, it assesses the correlations between my review scores and those of these various publications of film criticism.

<!-- These packages each enhanced the dataset by adding to it. At the introduction of each package, I attempted to leverage those added data elements in a new analysis. These analyses are presentably featured in the **Analysis (Jupyter NBs)** directory, in both *ipynb* and *html* files. These documents, which were deliberately written and organized with an interested reader in mind, might help to explain my project's structure and motivations.  -->

As a light disclaimer, I feel that these analyses of mine are much lighter than what my beloved database deserves. I intend to return and deepen my analysis, to better leverage the richness I've cultivated. But as of yet I've skimped on this, because analysis was rarely the primary focus for this project. Which brings me to my next point...


<br></br>
## This Project's Focus

Questions stemming from data analysis often guided this project, but such analysis was rarely its primary focus. **Rather, this project primarily involves data ingestion through web-scraping and other parsings of HTML, as well as some database management.** I have programmatically taken in data from several sources- my watchlist; the *OMDb*; and several online aggregators of film criticism- to create a rich and persistent dataset, aimed toward the prediction of ratings.


<br></br>

<a id="projects-course"></a>
### This Project's Course, in Subprojects

This project, which I started in Dec 2023, consists of several fairly expansive subprojects. The first of these involved parsing my movie list and loading it into a local MySQL database.

In the next subproject, I broadened that database by also loading records from the *OMDb*, which I found to be a rich, open source film database. 

That addition introduced film review scores to my database, onto which this project's focus then shifted. In the subproject following, I shored up the integrity of this review score data, by building processes to report its missing values and facilitate their remapping (in cases where the lack was erroneous.)

This led to a new subproject where I again broadened the database, this time by retrieving the scores of additional review sites. It involved building numerous web-scrapers for *Metacritic*, *Letterboxd*, and *RogerEbert*. 

Once satisfied, I followed webscraping to a different end: the retrieval of showtimes for Chicago's independent cinemas (which aren't covered by Fandango.) With these successfully retrieved, I then coded schedulers to slate them in Google Calendars, for my convenient reference. Though I have achieved these functionalities, I continue to work on this subproject, as I hope to add a couple additional cinemas, like FACETS and Logan Theatre.

If you would like a more detailed overview of how these subprojects connect, please see this [summary in markdown.](/Presentation/README_package_details.md).


<br></br>
## Legibility

To maximize the legibility of this project's code and findings, I have strove to document it thoroughly with explanation. Such explanation manifests in ample code comments, presentable notebook analyses, and *README* files like this one.


<br></br>
## Questions and Feedback

Please feel free to reach out to me with questions. I would also welcome and appreciate any feedback you might offer. If you do comment, please consider that this work is both ongoing and quite personal to me.

**Thank you for witnessing me,**

Movie-Mad Max
