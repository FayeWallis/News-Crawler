import pandas as pd
from datetime import datetime
from datetime import date
import newsfetch
from newsfetch.google import google_search
from newsfetch.news import newspaper
from pathlib import Path
import locationtagger
import requests
import nltk
import spacy
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
from tqdm import tqdm
import time
from collections import Counter
nltk.downloader.download('maxent_ne_chunker')
nltk.downloader.download('words')
nltk.downloader.download('treebank')
nltk.downloader.download('maxent_treebank_pos_tagger')
nltk.downloader.download('punkt')
nltk.download('averaged_perceptron_tagger')

#primary address list
addresses = [
'https://www.al.com/news/',
'https://www.adn.com/',
'https://www.azcentral.com/',
'https://www.hotsr.com/',
'https://www.mercurynews.com/',
'https://www.denverpost.com/',
'https://gazette.com/news/',
'https://www.courant.com/',
'https://www.delawareonline.com/',
'https://www.sun-sentinel.com/',
'https://www.ajc.com/',
'https://www.staradvertiser.com/',
'https://www.postregister.com/',
'https://www.chicagotribune.com/',
'https://www.indystar.com/',
'https://www.desmoinesregister.com/',
'https://www.cjonline.com/',
'https://www.courier-journal.com/',
'https://www.nola.com/',
'https://www.pressherald.com/',
'https://www.baltimoresun.com/',
'https://www.bostonglobe.com/',
'https://www.freep.com/',
'https://www.startribune.com/',
'https://www.clarionledger.com/',
'https://www.news-leader.com/',
'https://billingsgazette.com/',
'https://omaha.com/',
'https://www.reviewjournal.com/',
'https://www.unionleader.com/',
'https://www.app.com/',
'https://www.abqjournal.com/',
'https://buffalonews.com/',
'https://www.charlotteobserver.com/'
'https://bismarcktribune.com/',
'https://www.dispatch.com/',
'https://www.cincinnati.com/',
'https://www.oklahoman.com/',
'https://www.oregonlive.com/',
'https://www.bendbulletin.com/',
'https://www.inquirer.com/',
'https://www.providencejournal.com/',
'https://www.newportri.com/',
'https://www.postandcourier.com/',
'https://www.argusleader.com/',
'https://www.tennessean.com/',
'https://www.houstonchronicle.com/',
'https://www.sltrib.com/',
'https://www.burlingtonfreepress.com/',
'https://www.yakimaherald.com/'
'https://www.wvgazettemail.com/',
'https://www.jsonline.com/',
'https://trib.com/'
]

#initial search process, using only a single keyword tag
ingestion_log = pd.read_csv('ingestion_log.csv')

target_urls = []

for address in tqdm(addresses):
    try:
        google = google_search('transgender', address)
        most_recent = ingestion_log['article date'].max()
        for url in google.urls:
            news = newspaper(url)
            keywords = news.keywords
            pub_date = news.date_publish
            tags = ['trans', 'transgender', 'antitrans', 'violence', 'violent',
            'assault', 'murder', 'rape', 'intimidation', 'death',
            'killed', 'assaulted', 'raped', 'murdered', 'shot', 'abused']
            match_list = [x for x in keywords if x in tags]
            if len(match_list) != 0 and pub_date > most_recent:
                target_urls.append(url)          
    except: 
        continue

#more thorough second search, takes multiple keyword tags

summary_log = pd.read_csv('news_data.csv')
ingestion_log = pd.read_csv('ingestion_log.csv')
summary_data_all = []
ingestion_data_all = []

#finds and sorts Person Names in each article, assumes most common as Victim Name
def nametagger(x):
    names = []
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(x)
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            names.append(ent.text)
    if names == []:
        return 0
    else:
        victim = max(names,key=names.count)
        return victim
#cuts down bulk of articles to only those which contain relevant values
for url in tqdm(target_urls): 
        news = newspaper(url)
        text = news.headline + news.article
        article = text.split(' ')
        if text == '':
            continue
        article_date = news.date_publish[:10]
        try:
            year = news.date_publish[:4]
            place_entity = locationtagger.find_locations(text = text)
            state_list = place_entity.regions
            city_list = place_entity.cities
            state = max(state_list,key=state_list.count)
            if max(city_list,key=city_list.count) == state:
                city = 0
            else:
                city = max(city_list,key=city_list.count)
        except:
            continue
        tags = ['assault', 'murder', 'rape', 'intimidation', 'abuse', 
                'killed', 'assaulted', 'raped', 'murdered', 'abused', 
                'violence']
        severity_clues = [x for x in article if x in tags]
        if severity_clues == []:
            continue
        else:
            counter = Counter(severity_clues)
            most_common = counter.most_common(1)
            severity = most_common[0][0]
            name = nametagger(text)
            summary = [city, state, year, severity]
            today = date.today()
            ingestion_date = today.strftime("%m/%d/%Y")
            ingestion = [url, article_date, ingestion_date]
            summary_data_all.append(summary)
            ingestion_data_all.append(ingestion)

#concatenate old and new data, save to csv
df1 = pd.DataFrame(summary_data_all, columns=['City', 'State', 'Year', 'Severity'])
df2 = pd.DataFrame(ingestion_data_all, columns=['url', 'article date', 'ingestion date'])
df3 = pd.concat([df1, summary_log], ignore_index=True)
df4 = pd.concat([df2, ingestion_log], ignore_index=True)

filepath = Path('news_data.csv')  
filepath2 = Path('ingestion_log.csv')
filepath.parent.mkdir(parents=True, exist_ok=True)  
filepath2.parent.mkdir(parents=True, exist_ok=True)  
df3.to_csv(filepath, index=False) 
df4.to_csv(filepath2, index=False)
