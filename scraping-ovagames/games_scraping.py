import requests
from selectolax.parser import HTMLParser
import json
import os
import pandas as pd

# open html_page file

try:
    with open("./output/games.json", "r") as reading:
        games = json.load(reading)
except:
    games = {}

try:
    with open("./output/monitoring.json", "r") as reading:
        monitoring = json.load(reading)
except:
    monitoring = {}

for game, value in games.items():
    while True:
        if game in monitoring:
            if monitoring[game] == "[DONE]":
                # print("break")
                break

        page = requests.get(game)
        html = HTMLParser(page.content)

        try:
            title = html.css_first("#left-div > div:nth-child(2) > h1 > a").text(strip=True)
            img_title = html.css_first("#left-div > div:nth-child(2) > p:nth-child(4) > img").attributes["src"]
            desc = html.css("#wp-tabs-1 .wp-tab-content .wp-tab-content-wrapper")[0].text(strip=True)
            s_req = html.css("#wp-tabs-1 .wp-tab-content .wp-tab-content-wrapper")[2].text(strip=True)
            panduan = html.css("#wp-tabs-1 .wp-tab-content .wp-tab-content-wrapper")[4].text(strip=True)
            link_game = html.css("#wp-tabs-1 .wp-tab-content .wp-tab-content-wrapper .dl-wraps-item a")
            img_ss = html.css("#wp-tabs-1 .wp-tab-content .wp-tab-content-wrapper > img")
            details = html.css("#left-div > div:nth-child(2) > p")

            print(details[1].text())

            monitoring[game] = "[DONE]"

            with open("./output/monitoring.json", "w") as fileoutput:
                json.dump(monitoring, fileoutput)
        except:
            break

        #print(data.split('\n')[7].split(':')[1])
