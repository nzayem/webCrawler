import requests
import os
from bs4 import BeautifulSoup
import glob
from datetime import datetime
from fake_useragent import UserAgent
import pandas as pd
import sqlite3


# User agent:
ua = UserAgent()
random_agent = ua.random
header = {"User-Agent": random_agent}


def download_archive_page(page):

    filename = 'busnewsfr/page-%09d.html' % page

    if not os.path.isfile(filename):
        url = "https://www.businessnews.com.tn/liste/Dernieres_News/520/" + "%d" % page

        r = requests.get(url, headers=header)
        with open(filename, 'w+', encoding='utf-8') as f:
            f.write(r.text)


def parse_archive_page(file_page):

    with open(file_page, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    links = ["https://www.businessnews.com.tn/" + a['href']
             for a in soup.select("div.ligneListeArticle a.titreArticleListe")]

    return links


def download_article(url):

    url_text = url.split('/')[3].split(',')[0]

    # check if the article is already there
    filename = 'busnewsfr/raw_articles/' + url_text + '-article.html'

    if not os.path.isfile(filename):
        r = requests.get(url, headers=header)
        try:
            with open(filename, 'w+', encoding='utf-8') as f:
                f.write(r.text)
        except FileNotFoundError:
            # Reduce length of filenames exceeding the max allowed length.
            filename = 'busnewsfr/raw_articles/' + url_text[:100] + '-article.html'
            with open(filename, 'w+', encoding='utf-8') as f:
                f.write(r.text)


def parse_article(article_file):

    with open(article_file, "r", encoding='utf-8') as f:
        html = f.read()

    datum = {}

    soup = BeautifulSoup(html, 'html.parser')

    # adding the filename:
    datum['FileName'] = article_file

    # Canonical URL:
    datum['url'] = soup.find("link", {'rel': 'canonical'})['href']

    # Article Title:
    datum['headline'] = soup.title.text

    # Article text:
    art_container = soup.find('div', 'contTxt')
    p_list = art_container.find_all('p')
    art_text = ''
    for item in p_list:
        art_text += item.text
    datum['content'] = art_text

    # Date and Time details:
    str_date = soup.find('div', {'class': 'heureArticle fas fa-calendar'}).text
    try:
        art_date = datetime.strptime(str_date.strip().split()[0], "%d/%m/%Y")
    except ValueError:
        art_date = datetime.strptime('01/01/1900', "%d/%m/%Y")

    datum['date_time'] = art_date
    datum['day'] = art_date.date().strftime("%A")
    datum['month'] = art_date.date().strftime("%B")
    datum['year'] = art_date.year

    return datum


for i in range(1, 7801):
    download_archive_page(i)
    print(i)
print('Archive download Done')

article_urls = []
for page_file in glob.glob('busnewsfr/page-*.html'):
    article_urls += parse_archive_page(page_file)

with open('busnewsfr/articles_urls.txt', 'w', encoding='utf-8') as f:
    for url_address in article_urls:
        f.write(url_address + '\n')

# Reading the urls stored in the text files after pausing the crawling

with open('busnewsfr/articles_urls.txt', 'r', encoding='utf-8') as f:

    article_urls = [line.strip() for line in f]

print('Urls parsed successfully.... check the text file')

counter = 0
# Downloading Raw Articles
for link in article_urls:
    download_article(link)
    counter += 1
    print(link)
    print(f'Article n. {counter} downloaded')
print('Articles pages downloaded')

df = pd.DataFrame()
for article_html in glob.glob("busnewsfr/raw_articles/*-article.html"):
    print(article_html)
    df = df.append(parse_article(article_html), ignore_index=True)
    print(article_html + '....parsed successfully')

print('Dataframe created:')
print(df.info)

# Saving to database
db_name = 'bus_news.db'
con = sqlite3.connect(db_name)
df.to_sql('posts', con, index=False, if_exists="replace")
con.close()

print('Crawling operation completed successfully')
