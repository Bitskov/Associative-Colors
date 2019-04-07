import os
import sys
import pickle
import random

# Loading images
import requests
from PIL import Image
from io import BytesIO

# Text processing
import spacy
import re
from bs4 import BeautifulSoup

# Statistics
import time
from scipy import stats
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans

# Selenium
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


url = "https://duckduckgo.com/?q=%s&iar=images&iax=images&ia=images"


def parse_text(text):
    PUNCTUATION = {' ', ',', ';', ':', '-', '\n'}
    SENTENCE_SPLITERS = {'.', '!', '?'}

    text = text.lower()

    words = []

    word = ""
    for ch in text:
        if ch not in PUNCTUATION and ch not in SENTENCE_SPLITERS:
            word += ch
        else:
            if word:
                words.append(word)
            word = ""
    words.append(word)
    return words


def get_image_color(image):
    image = image.convert("RGB").resize((1, 1))
    color = list(image.getdata())
    return color


def get_word_links(word):
    driver.get("https://duckduckgo.com/?q=%s&iar=images&iax=images&ia=images" % word)
    src = driver.page_source
    parser = BeautifulSoup(src, "html.parser")
    img_tags = parser.findAll('img')
    links = []
    for img in img_tags:
        try:
            if not 'assets' in img['src'] and not 'ico' in img['src']:
                links.append(img['src'])
        except:
            pass

        if len(links) == 10:
            break
    return links


def get_word_colors(word):
    links = get_word_links(word)
    pixels = []
    for link in links:
        if link[:5] != 'https':
            link = 'https:' + link
        response = requests.get(link)
        img = Image.open(BytesIO(response.content))
        pixels.append(get_image_color(img))
    return pixels


# TODO: make every color unique
def get_word_color(word):
    if word in COLORS.keys():
        return COLORS[word]
    colors = get_word_colors(word)
    colors = np.array(sorted(colors))
    colors.resize(10, 3)
    km = KMeans(n_clusters=3)
    km.fit(colors)
    centers = km.cluster_centers_
    predicted = sorted(km.predict(colors))
    i = stats.mode(predicted).mode
    c = [int(j) for j in centers[i][0]]
    while c in COLORS.values():
        index = random.randint(0, 2)
        c[index] += random.randint(-2, 2)
    COLORS[word] = c
    return COLORS[word]


def get_fb2text(file):
    with open(file, 'r') as f:
        content = f.read()

    tags = []
    opening_tag = False
    closing_tag = False
    parsing_tag = False
    tag = ""
    text = ""

    for ch in content:
        if ch == '<':
            parsing_tag = True
            opening_tag = True
            continue
        if parsing_tag and ch == '/':
            opening_tag = False
            closing_tag = True
            continue
        if parsing_tag and ch == '>':
            if opening_tag:
                tags.append(tag)
            if len(tags) != 0 and closing_tag:
                t = tags.pop()
                if t == "p":
                    text += "."
            parsing_tag = False
            opening_tag = False
            closing_tag = False
            tag = ""
            continue
        if parsing_tag:
            tag += ch
            continue
        if len(tags) != 0 and tags[len(tags) - 1] == "p":
            text += ch
    return text


def get_books_files(dir):
    root_dir = dir
    files = []
    content = os.listdir(dir)
    for f in content:
        path = os.path.join(root_dir, f)
        if os.path.isfile(path):
            if '.fb2' in path:
                files.append(path)
        if os.path.isdir(path):
            for file in get_books_files(path):
                if '.fb2' in file:
                    files.append(file)
    return files


def save_dict():
    with open('colors.pkl', 'wb') as f:
        pickle.dump(COLORS, f)


if __name__ == '__main__':
    args = sys.argv
    if len(sys.argv) == 1:
        new_args = input()
        args.extend(new_args.split())

    command = args[1]
    if command == "--add-new-books":
        global driver, nlp, COLORS

        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        print('Webdriver is loaded')
        nlp = spacy.load('en_core_web_lg')
        print("Natural language processor is loaded")
        COLORS = {}

        parsed_books = set()

        # Loading existing data
        try:
            with open('parsed_books.pkl', 'rb') as f:
                parsed_books = pickle.load(f)
        except IOError:
            print("New parsed_books.pkl file has been created")

        try:
            with open('colors.pkl', 'rb') as f:
                COLORS = pickle.load(f)
        except IOError:
            print("New colors.pkl file has been created")

        books = get_books_files('books')
        books_to_parse = []
        for book in books:
            if book not in parsed_books:
                books_to_parse.append(book)

        for book in books_to_parse:
            print("Processing book \"%s\"" % book)
            words = [token.lemma_ for token in nlp(" ".join(parse_text(get_fb2text(book))))]
            for word in words:
                if word not in COLORS.keys():
                    start_time = time.time()
                    get_word_color(word)
                    end_time = time.time()
                    print("Query for word \"%s\" has taken %f seconds" % (word, end_time - start_time))
                    if len(COLORS.keys()) % 10 == 0:
                        print("CONGRATULATIONS DICT HAS REACHED THE SIZE OF %i" % len(COLORS.keys()))
                        save_dict()
            print("Book \"%s\" has been successfully parsed!" % book)
            parsed_books.add(book)

        driver.close()

        # Saving gotten data
        with open('parsed_books.pkl', 'wb') as f:
            pickle.dump(parsed_books, f)

        with open('colors.pkl', 'wb') as f:
            pickle.dump(COLORS, f)