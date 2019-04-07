import requests
from PIL import Image
import re
import matplotlib.pyplot as plt
from io import BytesIO
import numpy as np

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup


url = "https://duckduckgo.com/?q=%s&iar=images&iax=images&ia=images"
driver = webdriver.Firefox()
driver.close()


def get_image_color(image):
    image = image.resize((1, 1))
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
                links.append('https:' + img['src'])
        except:
            pass
    return links


def get_word_colors(word):
    links = get_word_links(word)
    pixels = []
    for link in links:
        response = requests.get(link)
        print(link)
        img = Image.open(BytesIO(response.content))
        print(img)
        img = img.convert("RGB").resize((100, 100,))
        pixels.append(get_image_color(img))
    return pixels


if __name__ == '__main__':
    link = "https://proxy.duckduckgo.com/iu/?u=https%3A%2F%2Ftse3.mm.bing.net%2Fth%3Fid%3DOIP.rH2WvQDk3zmLD-ZaLJRdJAHaGh%26pid%3DApi&f=1"
    img = Image.open(BytesIO(requests.get(link).content))
    pic = np.array(list(img.getdata()))
    print(pic.shape)