# Max's Movie List Project
## Data Ingestor and Ratings Predictor

### The Movie List

This is a multi-faceted personal project that centers on my personal moviegoing. I record this moviegoing in a document that functions as both a watchlist and a log. It resembles a to-do list, including movies both seen and unseen, as well as my ratings of the former.

My project starts with the parsing and loading of this list's data, into a dedicated, local MySQL database. From there, its course over the past year can be traced chronologically to these packages I've created...

### Custom Packages

1. **movielist_ingestion**: Automatically parse and load data from my movie list into a local MySQL database.

2. **omdb_builder**: Broaden this dataset by also loading in records from *The Open Movie Database (OMDb)*.

3. **critic_ratings.RatingsTableMender**: For the review scores provided in the *OMDb* data, programmatically report and remap values that might be missing erroneously.

4. **critic_ratings.scrapers**: Web-scrape  individual reviews from various critical publications which are aggregated to form a films "Metascore" on *Metacritic*. With these, I am able to analyze correlations between my ratings and those of prominent publications. 

    This package also includes scrapers that I've built for the sites *Letterboxd* and *RogerEbert*.

### Notebook Analyses

These packages each enhanced the dataset by adding to it. At the introduction of each package, I attempted to leverage those added data elements in a new analysis. These analyses are presentably featured in the **Analysis (Jupyter NBs)** directory, in both *ipynb* and *html* files. These documents, which were deliberately written and organized with an interested reader in mind, might help to explain my project's structure and motivations. 

As a light disclaimer, I feel that these analyses of mine are much lighter than what my beloved database deserves. I intend to return and deepen my analysis in ways that better leverage the richness I've cultivated. But I've yet skimped on this because analysis was rarely the primary focus for this project, which brings me to my next point...

## This Project's Focus

Questions stemming from data analysis often guided this project, but such analysis was rarely the primary focus of this exercise. Rather, **this project primarily involves data ingestion through web-scraping and other parsings of HTML, as well as some database management.** I have programmatically taken in data from several sources- my watchlist; the *OMDb*; and several various websites that aggregate film criticism- to create a rich and persistent dataset, aimed toward the prediction of ratings.

### Legibility

To maximize the legibility of this project's code and findings, I have attempted to thoroughly document it with explanation. Such explanation manifests in ample code comments, the notebook analyses, and *README* files like this one.

### Questions and Feedback

Please feel free to reach out to me with questions. I would also welcome and appreciate any feedback you might offer. If you do comment, please consider that this work is both ongoing and quite personal to me.

**Thank you!**

Max