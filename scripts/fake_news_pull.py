"""
Created on April 9, 2020

@author: Sunny Kwong
"""

import os
import sys
import urllib

from bs4 import BeautifulSoup
import newspaper
import pickle


def main():
    """This script generates our 'fake' articles for training"""

    # Pulls Articles
    real_news_article_pull = extract_real_true_news(1)
    empire_news_pull = extract_empire(1)
    onion_news_pull = extract_onion(1)

    if not os.path.exists('pickled_data'):
        os.mkdir('pickled_data')

    # Saves them in a pickled format in a folder.
    with open('pickled_data/real_news_article_pull.pickle', 'wb') as handle:
        pickle.dump(real_news_article_pull, handle)

    with open('pickled_data/empire_news_pull.pickle', 'wb') as handle:
        pickle.dump(empire_news_pull, handle)

    with open('pickled_data/onion_news_pull.pickle', 'wb') as handle:
        pickle.dump(onion_news_pull, handle)


def get_text_title_link(url):
    """
    Takes an article URL, and returns the article URL,
    Title, and text
    """

    # Checks just in case article can't be obtained
    try:
        article = newspaper.Article(url)
        article.download()
        article.parse()
    except newspaper.article.ArticleException:
        return
    return article.url, article.title, article.text


def extract_empire(max_page):
    """
    Extract articles from EmpireNews.net in the
    political section
    """

    all_links = {}

    for page in range(1, max_page+1):

        # Creates String of the page link we want
        page_link = "https://empirenews.net/category/politics/page/" + \
                    str(page)

        # Opens the page, gathers html and makes it a soup object
        empire_html = urllib.request.urlopen(page_link)
        empire_soup = BeautifulSoup(empire_html)

        # for every page, finds all tags with 'h2'
        # then finds the part of the tag with the 'a'
        # tag and extracts the link from the story
        for link in empire_soup.findAll('h1'):
            a_tag = link.find('a')
            if a_tag is not None:
                story_link = a_tag['href']
                # contains the text, title, and URL of the story
                story_obj = get_text_title_link(story_link)
                if story_obj is not None:
                    all_links[story_obj[0]] = {'text': story_obj[2],
                                               'title': story_obj[1]}

    return all_links


def extract_real_true_news(max_page):
    """
    Extract articles from realtruenews.org,
    a fake news website for politics
    """

    all_links = {}

    for page in range(0, max_page+1):
        # Creates String of the page link we want
        page_link = "http://www.realtruenews.org/home/page/" + str(page)

        # Opens the page, gathers html and makes it a soup object
        rtn_html = urllib.request.urlopen(page_link)
        rtn_soup = BeautifulSoup(rtn_html)

        txt_to_check = "www.realtruenews.org/single-post"

        # for every page, finds all tags with 'h2'
        # then finds the part of the tag with the 'a'
        # tag and extracts the link from the story
        for link in rtn_soup.findAll('a'):
            # checks if the tag has a link and the link starts with
            # the above text
            if link.has_attr('href') and txt_to_check in link['href']:
                story_link = link['href']
                # contains the text, title, and URL of the story
                story_obj = get_text_title_link(story_link)
                if story_obj is not None:
                    if not story_obj[1] in all_links:
                        all_links[story_obj[0]] = {'text': story_obj[2],
                                                   'title': story_obj[1]}
    return all_links


def extract_onion(max_page):
    """
    Extract articles from the onion
    """

    all_links = {}

    # page_link_upd will we the page we open
    # page_link is the string we will save to use over and over again
    page_link = "https://politics.theonion.com/"
    page_link_upd = "https://politics.theonion.com/"
    page_link_to_chk = "https://politics.theonion.com/c"

    for page in range(0, max_page):
        onion_html = urllib.request.urlopen(page_link_upd)
        # Delicious onion soup
        onion_soup = BeautifulSoup(onion_html)
        for link in onion_soup.findAll('a'):

            if link.has_attr('href') and \
                page_link in link['href'] and \
                    page_link_to_chk not in link['href']:
                story_link = link['href']
                # contains the text, title, and URL of the story
                story_obj = get_text_title_link(story_link)
                if story_obj is not None:
                    if story_obj[1] not in all_links:
                        all_links[story_obj[1]] = (story_obj[0],
                                                   story_obj[2])

            # For the next page, checks if the tag contains link
            # to the next page, if yes, make that the new page to
            # open
            elif link.has_attr('data-ga'):
                if link['data-ga'] == \
                   '[["Front page click","More stories click"]]':
                    page_link_upd = page_link + link['href']
    return all_links


if __name__ == '__main__':
    main()
