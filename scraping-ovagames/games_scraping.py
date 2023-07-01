import requests
from selectolax.parser import HTMLParser
import json
import os
import pandas as pd
import sys
import traceback

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


try:
    df_final = pd.read_csv("./output/data.csv")
except:
    df_final = pd.DataFrame()


for game, value in games.items():
    print(f"process game {game}")
    Title = []
    hero_image = []
    genre = []
    developer = []
    publisher = []
    release = []
    language = []
    file_size = []
    mirror = []
    req = []
    panduan_ = []
    desc_ = []
    ss_image = []
    link_games = []
    all_details = {}
    initial_state_details = [
        "Title",
        "Genre",
        "Developer",
        "Publisher",
        "Release Date",
        "Languages",
        "File Size",
        "Mirrors",
    ]
    while True:
        if game in monitoring:
            if monitoring[game] == "[DONE]":
                break

        page = requests.get(game)
        html = HTMLParser(page.content)

        try:
            img_title = html.css_first("#left-div > div:nth-child(2) > p:nth-child(4) > img").attributes["src"]
            desc = html.css("#wp-tabs-1 .wp-tab-content .wp-tab-content-wrapper")[0].text()
            s_req = html.css("#wp-tabs-1 .wp-tab-content .wp-tab-content-wrapper")[2].text()
            panduan = html.css("#wp-tabs-1 .wp-tab-content .wp-tab-content-wrapper")[4].text()
            details = html.css("#left-div > div:nth-child(2) > p")
            hero_image.append(img_title)

            detail_req = details[1].text().split("\n")

            for dt in detail_req:
                key = dt.split(":")[0].strip()
                all_details[key] = dt.split(":")[1]

            for c in initial_state_details:
                if c not in all_details:
                    all_details[c] = ""

            for key, value in all_details.items():
                if key == "Title":
                    Title.append(value.strip())
                if key == "Genre":
                    genre.append(value.strip())
                if key == "Developer":
                    developer.append(value.strip())
                if key == "Publisher":
                    publisher.append(value.strip())
                if key == "Release Date":
                    release.append(value.strip())
                if key == "Languages":
                    language.append(value.strip())
                if key == "File Size":
                    file_size.append(value.split("/")[0].strip())
                if key == "Mirrors":
                    mirror.append(value.strip())

            req.append(s_req)
            desc_.append(desc)
            panduan_.append(panduan)

            link_game = html.css("#wp-tabs-1 .wp-tab-content .wp-tab-content-wrapper .dl-wraps-item a")

            img_ss = html.css("#wp-tabs-1 .wp-tab-content .wp-tab-content-wrapper > img")

            if len(img_ss) == 0:
                img_ss_op = html.css("#wp-tabs-1 .wp-tab-content .wp-tab-content-wrapper > a img")
                preview_img_op = [img_p.attributes["src"] for img_p in img_ss_op]
                print("preview_img_op", preview_img_op)
            else:
                preview_img = [img.attributes["src"] for img in img_ss]
                print(preview_img, file=sys.stderr)

            if len(link_game) == 0:
                print("except")
                link_game_op = html.css("#wp-tabs-1 .wp-tab-content .wp-tab-content-wrapper > blockquote a")
                link_game_op_text = html.css(
                    '#wp-tabs-1 .wp-tab-content .wp-tab-content-wrapper [style="color: #ff0000; font-family: book antiqua,palatino,serif;"]'
                )
                link_op = {
                    link_game_op_text[i].text(): link_game_op[i].attributes["href"] for i in range(len(link_game_op))
                }
                print("link_op_game", link_game_op)
            else:
                link__ = {link.text(): link.attributes["href"] for link in link_game}

            if not link__:
                link_games.append(link_op)
            else:
                link_games.append(link__)

            if not preview_img:
                ss_image.append(preview_img_op)
            else:
                ss_image.append(preview_img)

            df = pd.DataFrame(
                {
                    "Title": Title,
                    "hero_image": hero_image,
                    "genre": genre,
                    "developer": developer,
                    "publisher": publisher,
                    "release_date": release,
                    "language": language,
                    "file_size": file_size,
                    "mirror": mirror,
                    "notes": panduan_,
                    "requirement": req,
                    "description": desc_,
                    "preview_image": ss_image,
                    "link_download": link_games,
                }
            )

            df_final = pd.concat([df, df_final])
            monitoring[game] = "[DONE]"

            df_final.to_csv("./output/data.csv", index=False)

            with open("./output/monitoring.json", "w") as fileoutput:
                json.dump(monitoring, fileoutput)
        except Exception as e:
            traceback.print_exc()
            print(f"gagal {e}")
            break
