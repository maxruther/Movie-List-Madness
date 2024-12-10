# Max's Movie List Project
## Data Ingestor and Ratings Predictor

### The Movie List

This is a multi-faceted personal project that centers on my personal moviegoing. I record this moviegoing in a document that functions as both a watchlist/queue and a log. It resembles a to-do list, including movies both seen and unseen, as well as my ratings of the former.

My project starts with the parsing and loading of this list's data, into a dedicated, local MySQL database. From there, its course over the past year can be chronologically traced to these packages I've created...

### Custom Packages

1. **movielist_ingestion**: Automatically parse and load data from my movie list into a local MySQL database.
2. **omdb_builder**: Broaden this dataset by also loading in records from *The Open Movie Database*.
3. **critic_ratings.RatingsTableMender**: For the review scores provided in the *OMDb* data, programmatically report and remap their erroneously missing values.
4. **critic_ratings.scrapers**: Web-scrape critics' individual reviews from Metacritic, to drill down on their aggregate score's correlation with my own ratings. This package also includes scrapers I've built for the sites *Letterboxd* and *RogerEbert*.

### Notebook Analyses

After each package's enhancement of the data, I attempted to leverage the added elements in a new analysis. These analyses are presentably featured in the **Analysis (Jupyter NBs)** directory, in ipynb and html files. These documents might help to explain the structure and motivations of my project. As a disclaimer, these analyses are much lighter than what my beloved database deserves- which brings me to my next point...

## This Project's Focus

Data analysis has often motivated this project, but that was never its primary focus. Rather, **this project primarily involves data ingestion through HTML parsing, as well as some database management.** I have programmatically taken in data from several sources- my watchlist; the *OMDb*; various aggregators of film criticism- to create a rich and persistent dataset, aimed towards the prediction of ratings.

### Legibility

To maximize the legibility of this project's code and findings, I have attempted to thoroughly document it with explanation. Such explanation might be formed in code comments, the notebook analyses, and *README* files like this one.

### Questions and Feedback

Please feel free to reach out to me with questions. I would also welcome and appreciate any feedback you might offer. If you do so comment, please consider that this work is both ongoing and also quite personal to me.

**Thank you!**

Max