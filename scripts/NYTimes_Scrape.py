"""
Created on April 9, 2020

@author: Kamron Afshar
"""

import sys
from requests import get
from bs4 import BeautifulSoup
from yanytapi import SearchAPI
from time import sleep
import pickle
import numpy as np


def main():
    """
    This script crawls the New York Times for text articles
    related to politics
    """
    apikey = "bQAQ1gaKiEonGwGdTMCnbgYa0nWCQDhc"
    api = SearchAPI(apikey)

    articles = generate_urls(api)

    extract_text(articles)

    print("NYTimes Crawl completed")


def generate_urls(api):
    """
    Generate URLS for articles with titles
    Split into two steps to circumvent crawling obstacles
    """
    full_article_list1 = []
    for i in range(15):
        sleep(np.random.choice(15))
        articles = api.search("", fq={"news_desk.contains": ["Politics"],
                                      "type_of_material.contains": [
                                          "An Analysis", "text", "news",
                                          "News Analysis"]},
                              begin_date="20180101", page=i)
        for art in articles:
            url = art.web_url
            title = art.headline["main"]
            full_article_list1.append({"url": url, "title": title})

    full_article_list2 = []

    for i in range(15, 30):
        sleep(np.random.choice(15))
        articles = api.search("", fq={"news_desk.contains": ["Politics"],
                                      "type_of_material.contains": [
                                          "An Analysis", "text", "news",
                                          "News Analysis"]},
                              begin_date="20180101", page=i)
        for art in articles:
            url = art.web_url
            title = art.headline["main"]
            full_article_list2.append({"url": url, "title": title})

    full_article_list = full_article_list1 + full_article_list2

    return full_article_list


def extract_text(full_article_list):
    """
    using beautiful soup to extract the text from these articles
    """

    for article in full_article_list:
        raw_html = get(article["url"])
        bs = BeautifulSoup(raw_html.text)
        doc_text = ""
        for para in bs.find_all("div", class_="css-53u6y8"):
            doc_text += para.text
        article["text"] = doc_text

    f = open("NYT300.pkl", "wb")
    pickle.dump(full_article_list, f)
    with open('NYT300.pkl', 'rb') as f:
        data = pickle.load(f)
    f.close()


if __name__ == '__main__':
    main()
