# (IN-PROGRESS) - Scraping and Scheduling Showtimes - Subproject #5
## *Scraping showtimes from the pages of independent movie theaters in Chicago, then scheduling them in Google Calendars.*

Fandango doesn't report the showtimes of Chicago's independent movie theaters, which are really its best ones. To supplement Fandango, I scrape showtimes from several such theaters and schedule them by inserting events into Google Calendars. **Though still in-progress,** these processes comprise the *its_showtimes* package.

- Each theater gets a separate calendar.
- The events' lengths match the runtimes of the films. (For previews, I will eventually add in 15 minutes of padding.)


<br></br>
<center><img src="../Presentation/pics for quick overview/5 - mb and siskel cals and scheduled.png" width="95%" height="20%"/> </center>
<br></br>


## Standing Goals:

- Add a couple more theaters, like those of FACETS and Logan.
- Add fandango, if I can do so in a way that doesn't absolutely flood the calendars.
- Store scraped showtimes in my MySQL movie database.
- Incorporate a model trained on my personal ratings, so that these processes could underscore the showtimes of movies predicted to be especially promising.

