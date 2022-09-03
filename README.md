This crawler is based on the spider in the book blueprints for text analytics. I have used it to crawl the following news website: https://www.businessnews.com.tn/
The spider have the following functionalities:
-	Download the index pages (total 7800 pages), each page has around 10 articles. Number of pages can be defined when calling the related function: def download_archive_page(page):

-	Parse each page to download individual articles for a total of 77576 articles using the functions def parse_archive_page(file_page) and def download_article(url)

-	Parse each article page to get details like title, date, and content… using the function def parse_article(article_file):

-	Store the results in an SQLite database for further stats and NLP processing.

-	The spider could be stopped and will resume the download or parsing the content where it was stopped without raising an error or duplication.

Downloading the html files was to reduce requests sent to the website and avoid being blocked by the website. A Fake user agent is also used. 

This was a tedious task. Downloading and parsing 76000+ webpage took days. Needed also to adjust the parsing function to adapt to the changing html tags. Empty content text was easy to identify using pandas.

But the effort was worth it. Got 15 years of news content stored on local machine to be processed using NLP techniques and machine learning projects.

The spider could be used on any website, just by adjusting the html tags.

Below the number of articles per each year:

<img src="https://github.com/nzayem/webCrawler/blob/master/ArticlesYear.png">
