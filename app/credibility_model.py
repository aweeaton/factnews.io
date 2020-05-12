import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn import linear_model
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB
from collections import namedtuple
from lexical_diversity import lex_div as ld
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from lexicalrichness import LexicalRichness
from bs4 import BeautifulSoup
import pandas as pd
import string
import re
import nltk
import newspaper
from joblib import dump, load
import pickle
import tldextract
import googlesearch
import requests
import os

this_directory = os.path.dirname(__file__)

text_feature_clf = load(os.path.join(
    this_directory, 'static/models/rf_model_final.joblib'))
domain_clf = pickle.load(open(os.path.join(
    this_directory, 'static/models/domain_model'), 'rb'))
links_vocab = pickle.load(open(os.path.join(
    this_directory, 'static/models/links_vocab'), 'rb'))
count_vectorizer = pickle.load(open(os.path.join(
    this_directory, 'static/models/count_vec'), 'rb'))
model_count = pickle.load(open(os.path.join(
    this_directory, 'static/models/model_kaggle'), 'rb'))
tfidf_vectorizer = pickle.load(open(os.path.join(
    this_directory, 'static/models/tfidf'), 'rb'))
model_tfidf = pickle.load(open(os.path.join(
    this_directory, 'static/models/model_tfidf'), 'rb'))

# Route nltk data path
nltk.data.path.append('/tmp/')


def pos(pos_list):
    """POS tagging"""
    mapping = {'NOUN': 0, 'VERB': 0, '.': 0,
               'ADP': 0, 'DET': 0, 'ADJ': 0,
               'PRT': 0, 'ADV': 0, 'PRON': 0,
               'CONJ': 0, 'NUM': 0, 'X': 0}

    for item in pos_list:
        # print(item)
        mapping[item[0]] += item[1]
    return mapping


def preprocess(df_total):
    """Preprocessing article text : avergae length of sentence,
     frequency of tags, POS tagging"""
    # Cleaning text
    df_total["text"] = df_total.text.apply(lambda x: x.lower())
    # table = str.maketrans('', '', string.punctuation)
    # df_total["text"] = df_total.text.apply(lambda x: x.translate(table))
    df_total["text"] = df_total.text.apply(lambda x: re.sub(r'\d+', 'num', x))

    # substituting "U.S."
    df_total["little_clean"] = df_total.text.apply(
        lambda x: re.sub("U.S.", "United States", x))

    # cleaning text
    table_ = str.maketrans('', '')
    df_total['cleaned_text'] = df_total.text.str.translate(table_)

    # *******SYNTACTIC FEATURES *******#

    # splitting articles into sentences
    df_total["sentences"] = df_total.little_clean.str.split("\. ")

    # calculating num of sentences in each article
    df_total["num_of_sentences"] = df_total.sentences.apply(lambda x: len(x))

    # average length of sentences
    df_total["avg_sentence_length"] = df_total.sentences.apply(
        lambda x: round(np.mean([len(item) for item in x])))

    # POS Tagging
    df_total['POS_tags'] = df_total.cleaned_text.apply(
        lambda x: nltk.pos_tag(nltk.word_tokenize(x), tagset='universal'))

    # frequency of tags
    df_total["tag_fq"] = df_total.POS_tags.apply(
        lambda x: nltk.FreqDist(tag for (word, tag) in x))

    # count of each tag in each article
    df_total['Noun'] = df_total.tag_fq.apply(
        lambda x: pos(x.most_common())['NOUN'])
    df_total['Verb'] = df_total.tag_fq.apply(
        lambda x: pos(x.most_common())['VERB'])
    df_total['Punctuation'] = df_total.tag_fq.apply(
        lambda x: pos(x.most_common())['.'])
    df_total['Adposition'] = df_total.tag_fq.apply(
        lambda x: pos(x.most_common())['ADP'])
    df_total['Determiner'] = df_total.tag_fq.apply(
        lambda x: pos(x.most_common())['DET'])
    df_total['Adjective'] = df_total.tag_fq.apply(
        lambda x: pos(x.most_common())['ADJ'])
    df_total['Particle'] = df_total.tag_fq.apply(
        lambda x: pos(x.most_common())['PRT'])
    df_total['Adverb'] = df_total.tag_fq.apply(
        lambda x: pos(x.most_common())['ADV'])
    df_total['Pronoun'] = df_total.tag_fq.apply(
        lambda x: pos(x.most_common())['PRON'])
    df_total['Conjunction'] = df_total.tag_fq.apply(
        lambda x: pos(x.most_common())['CONJ'])
    df_total['Numeral'] = df_total.tag_fq.apply(
        lambda x: pos(x.most_common())['NUM'])
    df_total['Other'] = df_total.tag_fq.apply(
        lambda x: pos(x.most_common())['X'])

    # *********LEXICAL FEATURES **********#

    # word count
    df_total['characters_count'] = df_total.text.str.len()

    # Filtering only large texts
    df_total = df_total.loc[df_total.characters_count >= 100]

    # word average
    df_total['word_average'] = df_total['text'].apply(
        lambda x: np.mean([len(w) for w in x.split(' ')]))

    # lexical diversity
    df_total['lexical_diversity'] = df_total.text.apply(
        lambda x: ld.ttr([w for w in x.split(' ')]))

    # lexical richness
    df_total['lex_words'] = df_total.text.apply(
        lambda x: LexicalRichness(x).words)
    df_total['lex_uniquewords'] = df_total.text.apply(
        lambda x: LexicalRichness(x).terms)
    df_total['lex_ttr'] = df_total.text.apply(
        lambda x: LexicalRichness(
            x).ttr)  # type token ratio : lexical richness

    # *********PSYCOLINGUISTIC FEATURES **********#

    # Sentiment score
    analyser = SentimentIntensityAnalyzer()
    df_total['sentiment_score'] = df_total.text.apply(
        lambda x: analyser.polarity_scores(x)['compound'])

    return df_total


def text_features_model(text):
    """ Predicting how real an article is based on psycolinguistic, lexical and
    syntactic features of the article text

    Input: Article Text
    Output: Percentage of how real the article is
    """

    df_test = pd.DataFrame(data=[text], columns=['text'])
    df_test = preprocess(df_test)
    df_test = df_test.drop(['text', 'little_clean', 'sentences',
                            'cleaned_text', 'POS_tags', 'tag_fq'], axis=1)
    X_test = np.array(df_test)
    result = text_feature_clf.predict_proba(X_test)[0][0]
    return result * 100


def encode_link(link):
    """ Encodes domain names based on vocab"""
    if (link in links_vocab.keys()):
        return links_vocab[link]
    return -1


def google_query(query, num_results=10, header={'User-agent': 'your bot 0'}):
    """ Queries article title on google and returns domain of top 10 results"""
    query_str = query.replace(" ", "+")
    site = 'https://www.google.com/search?q=' + query
    search_page = requests.get(site, headers=header)
    search_soup = BeautifulSoup(search_page.text)
    links = search_soup.findAll("a")
    all_links = []
    for link in search_soup.find_all(
            "a", href=re.compile("(?<=/url\?q=)(htt.*://.*)"))[0:num_results]:
        all_links.extend(
            re.split(":(?=http)", link["href"].replace("/url?q=", "")))
    result = [encode_link(tldextract.extract(link).domain)
              for link in all_links]
    return pd.DataFrame(result).T


def domain_model(title):
    """ Predicting  how real an article is based on the
        top 10 domains obtained by google searching the title"""

    test_df = google_query(title)
    result = domain_clf.predict_proba(test_df)[0][1]
    return result * 100


def process_data_count(text):
    """
    Process data for count_vec model
    """
    text = pd.Series(text)
    text = text.fillna('')
    test_counts = count_vectorizer.transform(text.values)
    return test_counts


def predict_count(text):
    """
    Predict based on count vec model
    """
    cred_score = model_count.predict_proba(process_data_count(text))[0][0]
    return round(cred_score, 2)


def process_data_tfidf(text):
    """
    Process data for tfidf model
    """
    text = pd.Series(text)
    text = text.fillna('')
    test_counts = tfidf_vectorizer.transform(text.values)
    return test_counts


def predict_tfidf(text):
    """
    Predict based on tfidf vec model
    """
    cred_score = model_tfidf.predict_proba(process_data_tfidf(text))[0][0]
    return round(cred_score, 2)


def predict_credibility(text):
    """Predicts the credibility score of given article,
     weighted average of countvec model and tfidf model"""

    # feature_result = text_features_model(text)
    # domain_result = domain_model(title)
    # return int(0.5*feature_result + 0.5*domain_result)
    model_count_result = predict_count(text)
    model_tfidf_result = predict_tfidf(text)
    return round(100 * (0.5 * model_count_result + 0.5 * model_tfidf_result),
                 2)


def sentiment(text):
    """
    Returns negative sentiment score and warns user of highly negative text
    :param text: text from article
    :return: negative sentiment score
    """
    # Create a SentimentIntensityAnalyzer object.
    sid_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sid_obj.polarity_scores(text)

    # return negative sentiment
    return round(sentiment_dict['neg'] * 100, 1)
