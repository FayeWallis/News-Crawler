# News-Crawler
Scrape the archives of any news outlet for articles with target keywords.
Input the home page url of any news outlet into the NewsCrawler, along with any number of searchable keywords
It will return the urls of every article within that outlet's archives that match your keywords.  
This process will return a broad scope of articles with varying relevancy, but a second process is included
which sorts the first list of urls with a more fine toothed comb, numerically determining article relevance,
and saving relevant data from each article to a succinct pandas dataframe.

For the purposes of my example project, I was searching for articles regarding violence against the
transgender community in america.  The first process returned a bulk of over 1600 articles relating to
trans life in the US, but most of them were more focused on bathroom bills and sports bans than actual instances of violence.
The second process added more specific keywords, and searched for victim names and locations as well, 
filtering those 1600 articles down to roughly 300 that included every aspect I was looking for:
-Location
-Victim name
-Date
-Incident Severity

The NewsCrawler is currently tuned to this particular subject matter, but it can easily be altered to scrape 
for any sort of article criteria one could want.
