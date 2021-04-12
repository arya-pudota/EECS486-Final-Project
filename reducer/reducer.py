#Final Project for EECS 486

import requests
import spacy
from sys import argv
from bs4 import BeautifulSoup
from math import log

nlp = spacy.load('en_core_web_sm')


def parse_article_content(url):
    """
    Parses an article that is linked to by the url argument, and returns the data present
    :param url: url that links to the news article from which content must be retrieved
    :return: string containing the contents of the news article linked to by url
    """
    r = requests.get(url, headers = {
        "user-agent": "eecs486-tmd-bot",
        "from": "pudota@umich.edu"
    })
    soup = BeautifulSoup(r.text, "html.parser")
    heading = soup.find('h1', attrs={'class': 'entry-title'}).text.strip('\n')
    content = soup.find('div', attrs={'class': 'entry-content'}).text.strip('\n')
    return heading, content


def tokenize_sentence():
    """
    Parses the url that is given as an argument at the command line and returns a list containing the sentences present
    in the article.
    :return: list containing sentences that are in the article, original text
    """
    url = argv[1]
    heading, contents_text = parse_article_content(url)
    content_sents = list(nlp(contents_text).sents)
    return content_sents, contents_text


def build_correlation_matrix(content_sents):
    sentence_scores = {}
    for sentence_considered_index in range(len(content_sents)):
        sentence_considered = set(content_sents[sentence_considered_index])
        score = 0
        for sentence_checked_index in range(len(content_sents)):
            if sentence_considered_index != sentence_checked_index:
                sentence_check = set(content_sents[sentence_checked_index])
                for token_1 in sentence_considered:
                    for token_2 in sentence_check:
                        if not token_1.is_punct and not token_1.is_stop and not token_2.is_punct and not token_2.is_stop:
                            if str(token_1.lemma_) == str(token_2.lemma_):
                                score += 1
        sentence_scores[sentence_considered_index] = {
            'sentence': content_sents[sentence_considered_index],
            'score': score
        }
    top_sentences = sorted(sentence_scores.items(), key=lambda item: item[1]['score'], reverse=True)
    final_sentences = list()
    max_length = 350 #value defined given average reading spead of 250 wpm, spacy also accounts for punctuations, hence we selected
    for sentence in top_sentences:
        if max_length > len(sentence[1]['sentence']):
            final_sentences.append(sentence)
            max_length -= len(sentence[1]['sentence'])
        else:
            break
    final_sentences = tuple(final_sentences)
    ordered_final_sentences = sorted(final_sentences, key=lambda item: item[0])
    first_sentence_included = False
    for sentence in ordered_final_sentences:
        print(str(sentence[1]['sentence']).strip())

def build_pos_analysis(sentences):
    pos_sentence_dict = {}
    pos_text_dict = {}
    sentences, text = tokenize_sentence()
    sentence_position = 0
    for sentence in sentences:
        sentence_position += 1
        for token in sentence:
            if not token.is_punct and not token.is_stop:
                lemma = token.lemma_
                pos = token.pos_
                if sentence not in pos_sentence_dict:
                    pos_sentence_dict[sentence] = dict()
                    pos_sentence_dict[sentence]["SENTENCE_POSITION"] = sentence_position
                if pos not in pos_sentence_dict[sentence]:
                    pos_sentence_dict[sentence][pos] = dict()
                if lemma not in pos_sentence_dict[sentence][pos]:
                    pos_sentence_dict[sentence][pos][lemma] = 1
                else:
                    pos_sentence_dict[sentence][pos][lemma] += 1
                if pos not in pos_text_dict:
                    pos_text_dict[pos] = dict()
                if lemma not in pos_text_dict[pos]:
                    pos_text_dict[pos][lemma] = 1
                else:
                    pos_text_dict[pos][lemma] += 1
    return pos_text_dict, pos_sentence_dict


def score_sentences(pos_text_dict, pos_sentence_dict):
    sentence_scores = {}
    for sentence in pos_sentence_dict:
        score = 0
        if 'PROPN' in pos_sentence_dict[sentence]:
            for token in pos_sentence_dict[sentence]['PROPN']:
                score += 1 * log(pos_text_dict['PROPN'][token] * pos_sentence_dict[sentence]['PROPN'][token])
        if 'VERB' in pos_sentence_dict[sentence]:
            for token in pos_sentence_dict[sentence]['VERB']:
                score += 1 * log(pos_text_dict['VERB'][token] * pos_sentence_dict[sentence]['VERB'][token])
        if 'NOUN' in pos_sentence_dict[sentence]:
            for token in pos_sentence_dict[sentence]['NOUN']:
                score += 1 * log(pos_text_dict['NOUN'][token] * pos_sentence_dict[sentence]['NOUN'][token])
        sentence_scores[sentence] = score
    return sentence_scores


def summarized_article(sentence_scores):
    sorted_sentences = sorted(sentence_scores.items(), key=lambda item: item[1], reverse=True)
    max_length = 250
    summary = dict()
    for sentence_score in sorted_sentences:
        sentence_order = pos_sentence_dict[sentence_score[0]]["SENTENCE_POSITION"]
        sentence = str(sentence_score[0])
        new_sentence = ""
        for token in sentence_score[0]:
            #TODO: Figure out how to reduce the length of the chosen sentences
            if token.pos_ not in {"DT"}:
                new_sentence += str(token) + " "
        summary[sentence_order] = new_sentence
        max_length -= len(new_sentence.split())
        if max_length <= 0:
            break
    sorted_summary = sorted(summary.items(), key=lambda item: item[0])
    final_summary = ""
    for sentence in sorted_summary:
        final_summary += sentence[1]
    print(final_summary)

if __name__ == "__main__":
    # sentences = tokenize_sentence()
    # pos_text_dict, pos_sentence_dict = build_pos_analysis(sentences)
    # sentence_scores = score_sentences(pos_text_dict, pos_sentence_dict)
    # summarized_article(sentence_scores)
    content_sents, contents_text = tokenize_sentence()
    build_correlation_matrix(content_sents)