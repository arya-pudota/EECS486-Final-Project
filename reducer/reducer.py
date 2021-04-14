#Final Project for EECS 486

import requests
import spacy
from bs4 import BeautifulSoup
import re

nlp = spacy.load('en_core_web_sm')
pos_tags = {"NOUN", "PROPN", "ADJ"}


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
    heading = soup.find('h1', attrs={'class': 'entry-title'}).text.strip()
    content = soup.find('div', attrs={'class': 'entry-content'}).text.strip('\n')
    content = re.sub('\n', ' ', content)
    content = re.sub('-', '', content)
    return heading, content


def tokenize_sentence(contents_text):
    """
    Parses the url that is given as an argument at the command line and returns a list containing the sentences present
    in the article.
    :return: list containing sentences that are in the article, original text
    """
    content_sentences = list(nlp(contents_text).sents)
    return content_sentences, contents_text


def build_node_dictionary(content_sentences):
    """
    Builds the set of nodes that will be considered when building the TextRank graph for score calculations.
    :param content_sentences:
    :return: a dictionary containing all nodes and their initialized scores
    """
    nodes_to_be_considered = dict()
    for sentence in content_sentences:
        for token in sentence:
            if not token.is_punct and not token.is_stop and token.pos_ in pos_tags:
                nodes_to_be_considered[str(token.lemma_.lower())] = 1
    return nodes_to_be_considered


def build_textrank_graph(content_sentences):
    """
    Builds the TextRank graph that will be used to calculate scores for all of the nodes in the graph. Uses
    co-occurrence of lexical units in a 3-word window, excluding punctuations and stop-words
    :param content_sentences:
    :return: graph: dictionary containing all the nodes and edges for the node, nodes_to_be_considered: dictionary
    containing all the nodes in the graph and the corresponding initalized TextRank scores
    """
    graph = {}
    nodes_to_be_considered = build_node_dictionary(content_sentences)
    for sentence in content_sentences:
        tokens = []
        for token in sentence:
            x = token.pos_
            if not token.is_punct and not token.is_stop and token.pos_ in pos_tags:
                tokens.append(str(token.lemma_.lower()))
        for token_index in range(len(tokens)-1):
            token_1 = tokens[token_index]
            token_2 = tokens[token_index+1]
            if token_1 not in graph:
                graph[token_1] = {}
                graph[token_1]["textrank"] = 0.25
                graph[token_1]["successors"] = []
                graph[token_1]["predecessors"] = []
            if token_2 not in graph:
                graph[token_2] = {}
                graph[token_2]["textrank"] = 0.25
                graph[token_2]["successors"] = []
                graph[token_2]["predecessors"] = []
            graph[token_1]["successors"].append(token_2)
            graph[token_2]["predecessors"].append(token_1)
    for token in nodes_to_be_considered:
        if token not in graph:
            graph[token] = {}
            graph[token]["textrank"] = 0.25
            graph[token]["successors"] = []
            graph[token]["predecessors"] = []
    return graph, nodes_to_be_considered


def calculate_textrank(graph, nodes_to_be_considered):
    """
    Uses the TextRank algorithm (https://web.eecs.umich.edu/~mihalcea/papers/mihalcea.emnlp04.pdf) in order to build
    the TextRank of all nodes present in the graph entered as an argument.
    :param graph:
    :param nodes_to_be_considered:
    :return: nodes_to_be_considered: a dictionary containing all of the nodes with their final TextRank scores.
    """
    damping = 0.85
    max_diff = 1
    convergence = 0.001
    while max_diff > convergence:
        max_diff = 0
        for vertex in nodes_to_be_considered:
            old_textrank = graph[vertex]["textrank"]
            text_sum = 0
            for pre_vertex in graph[vertex]["predecessors"]:
                text_sum += 1 / len(graph[pre_vertex]["successors"]) * graph[pre_vertex]["textrank"]
            new_textrank = (1 - damping) / len(nodes_to_be_considered) + damping * text_sum
            if abs(new_textrank - old_textrank) > max_diff:
                max_diff = abs(new_textrank - old_textrank)
            graph[vertex]["textrank"] = new_textrank
            nodes_to_be_considered[vertex] = new_textrank
    return nodes_to_be_considered


def build_correlation_scores(content_sentences, nodes_to_be_considered):
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
                        if not token_1.is_punct and not token_1.is_stop and token_1.pos_ in pos_tags\
                                and not token_2.is_punct and not token_2.is_stop and token_2.pos_ in pos_tags:
                            if str(token_1.lemma_.lower()) == str(token_2.lemma_.lower()):
                                score += nodes_to_be_considered[str(token_1.lemma_.lower())]
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
    max_length = 250
    for sentence in top_sentences:
        for token in sentence[1]['sentence']:
            if not token.is_punct:
                max_length -= 1
        if max_length >= 0:
            final_sentences.append(sentence)
        else:
            break
    final_sentences = tuple(final_sentences)
    ordered_final_sentences = sorted(final_sentences, key=lambda item: item[0])
    summary = ""
    for sentence in ordered_final_sentences:
        summary += str(sentence[1]['sentence']).strip() + "\n"
    return summary


def return_summary(url):
    heading, content = parse_article_content(url)
    content_sentences, content_text = tokenize_sentence(content)
    graph, nodes_to_be_considered = build_textrank_graph(content_sentences)
    textrank_scores = calculate_textrank(graph, nodes_to_be_considered)
    sentence_scores = build_correlation_scores(content_sentences, textrank_scores)
    return {
        "url": url,
        "heading": heading,
        "content": select_top_sentences(sentence_scores)
    }


if __name__ == "__main__":
    while True:
        choice = input("Enter choice: '1' -> URL, '2'-> text, or enter 'exit': ")
        if choice == 'exit':
            break
        try:
            if int(choice) == 1:
                url = input("Enter URL here, or enter 'exit': ")
                if url == "exit":
                    break
                try:
                    heading, content = parse_article_content(url)
                    content_sentences, content_text = tokenize_sentence(content)
                    graph, nodes_to_be_considered = build_textrank_graph(content_sentences)
                    textrank_scores = calculate_textrank(graph, nodes_to_be_considered)
                    sentence_scores = build_correlation_scores(content_sentences, textrank_scores)
                    print(heading)
                    print()
                    print(select_top_sentences(sentence_scores))
                except:
                    print("Invalid URL!")
            if int(choice) == 2:
                content = input("Enter content here, or enter 'exit': ")
                content_sentences, content_text = tokenize_sentence(content)
                graph, nodes_to_be_considered = build_textrank_graph(content_sentences)
                textrank_scores = calculate_textrank(graph, nodes_to_be_considered)
                sentence_scores = build_correlation_scores(content_sentences, textrank_scores)
                print()
                print("Compressed Text:")
                print(select_top_sentences(sentence_scores))
        except ValueError or TypeError:
            print("Invalid Input! Try Again.")

