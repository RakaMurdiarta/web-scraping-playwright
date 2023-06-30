import requests
from selectolax.parser import HTMLParser
import json
import pandas as pd
import os
import math

base_url = "https://www.ovagames.com/"
categories_url = "https://www.ovagames.com/category/action"
page_url = "https://www.ovagames.com/category/action/page/1"
url_game = "https://www.ovagames.com/state-of-decay-2-juggernaut-edition-multi8-elamigos.html"

path_folder = "./checkpoint"


def read_json():
    state = {}
    json_files = [file for file in os.listdir(path_folder) if file.endswith(".json")]

    for file in json_files:
        join_path = os.path.join(path_folder, file)
        with open(join_path, "r") as json_f:
            data = json.load(json_f)
            state[file.replace(".json", "").replace("data-", "")] = len(data)

    return state


page = requests.get(base_url)

html = HTMLParser(page.text)

get_list_categories = html.css("div#categories > ul > li > a")

temp_categories = [category.attributes["href"] for category in get_list_categories]

state = read_json()
print(state)
for category_game in temp_categories:
    print(f"process {category_game}")

    page_categories = requests.get(url=category_game)
    html_categories = HTMLParser(page_categories.text)

    get_pages = html_categories.css_first("span.pages").text()
    pages = get_pages

    get_actual_number = int(pages.split(" ")[-1])
    category_game_text = category_game.split("/")[-1]
    while True:
        state = read_json()
        link = {}
        if category_game_text in state:
            if get_actual_number == math.ceil(state[category_game_text] / 14):
                print("already collcet")
                break

        for link_page in range(1, get_actual_number + 1):
            page_title = requests.get(url=f"https://www.ovagames.com/category/action/page/{link_page}")
            html_link_title = HTMLParser(page_title.text)
            get_link_titles = html_link_title.css("div.home-post-wrap div > h2 > a")
            link_titles = [linkes.attributes["href"] for linkes in get_link_titles]

            for link_title in link_titles:
                # print(f"get data {link_title}")
                link[link_title] = category_game_text

        with open(f"checkpoint/data-{category_game_text}.json", "w") as outfile:
            json.dump(link, outfile)
