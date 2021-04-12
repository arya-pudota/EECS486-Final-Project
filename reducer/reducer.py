#Final Project for EECS 486

import requests
import spacy
from sys import argv
from bs4 import BeautifulSoup
from math import log

nlp = spacy.load('en_core_web_sm')

def parse_article_content(url):
    """
    Parses a Michigan Daily article that is linked to by the url argument, and returns the data present
    :param url: url that links to the news article from which content must be retrieved
    :return: string containing the contents of the news article linked to by url
    """
    r = requests.get(url, headers={
        "user-agent": "eecs486-tmd-bot",
        "from": "pudota@umich.edu"
    })
    soup = BeautifulSoup(r.text, "html.parser")
    heading = soup.find('h1', attrs={'class': 'entry-title'}).text.strip('\n')
    content = soup.find('div', attrs={'class': 'entry-content'}).text.strip('\n')
    return heading, content


def tokenize_sentence(url):
    """
    Parses the url that is given as an argument at the command line and returns a list containing the sentences present
    in the article.
    :return: list containing sentences that are in the article, original text
    """
    heading, contents_text = parse_article_content(url)
    content_sentences = list(nlp(contents_text).sents)
    return content_sentences, contents_text


def build_correlation_scores(content_sentences):
    """
    Builds a correlation dictionary that compares sentences to other sentences in the article, performs cosine-similarity
    calculations using the Bag of Words model and computes the outcome for all sentences stored in the dictionary
    :param content_sentences:
    :return: dictionary containing correlation scores for all sentences
    """
    sentence_scores = {}
    for sentence_considered_index in range(len(content_sentences)):
        sentence_considered = set(content_sentences[sentence_considered_index])
        score = 0
        for sentence_checked_index in range(len(content_sentences)):
            if sentence_considered_index != sentence_checked_index:
                sentence_check = set(content_sentences[sentence_checked_index])
                for token_1 in sentence_considered:
                    for token_2 in sentence_check:
                        if not token_1.is_punct and not token_1.is_stop and not token_2.is_punct and not token_2.is_stop:
                            if str(token_1.lemma_) == str(token_2.lemma_):
                                score += 1
        sentence_scores[sentence_considered_index] = {
            'sentence': content_sentences[sentence_considered_index],
            'score': score
        }
    return sentence_scores


def select_top_sentences(sentence_scores):
    """
    Selects the top sentences from the sentence scores computed, up until the maximum length of the article (250 words)
    Once we select them, we then re-sort the sentences to appear in the order in which they are present in the original
    text.
    :param sentence_scores:
    :return:
    """
    top_sentences = sorted(sentence_scores.items(), key=lambda item: item[1]['score'], reverse=True)
    final_sentences = list()
    # value defined given average reading speed of 250 wpm, SpaCy also accounts for punctuations, hence we selected
    max_length = 350
    for sentence in top_sentences:
        if max_length > len(sentence[1]['sentence']):
            final_sentences.append(sentence)
            max_length -= len(sentence[1]['sentence'])
        else:
            break
    final_sentences = tuple(final_sentences)
    ordered_final_sentences = sorted(final_sentences, key=lambda item: item[0])
    summary = ""
    for sentence in ordered_final_sentences:
        summary += str(sentence[1]['sentence']).strip()
    return summary
