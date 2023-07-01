import requests
from selectolax.parser import HTMLParser
import json
import os
import pandas as pd
import sys

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
    while True:
        if game in monitoring:
            if monitoring[game] == "[DONE]":
                break

        page = requests.get(game)
        html = HTMLParser(page.content)

        try:
            title = html.css_first("#left-div > div:nth-child(2) > h1 > a").text(strip=True)
            img_title = html.css_first("#left-div > div:nth-child(2) > p:nth-child(4) > img").attributes["src"]
            desc = html.css("#wp-tabs-1 .wp-tab-content .wp-tab-content-wrapper")[0].text()
            s_req = html.css("#wp-tabs-1 .wp-tab-content .wp-tab-content-wrapper")[2].text()
            panduan = html.css("#wp-tabs-1 .wp-tab-content .wp-tab-content-wrapper")[4].text()

            link_game = html.css("#wp-tabs-1 .wp-tab-content .wp-tab-content-wrapper .dl-wraps-item a")
            print(f"link_game {link_game}")
            img_ss = html.css("#wp-tabs-1 .wp-tab-content .wp-tab-content-wrapper > img")

            print(f"img_ss {img_ss}")

            if len(img_ss) == 0:
                img_ss_op = html.css("#wp-tabs-1 .wp-tab-content .wp-tab-content-wrapper > a img")
                preview_img_op = [img_p.attributes["src"] for img_p in img_ss_op]
                print("preview_img_op", preview_img_op)

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
            details = html.css("#left-div > div:nth-child(2) > p")
            detail_req = details[1].text().split("\n")

            Title.append(title)
            hero_image.append(img_title)
            genre.append(detail_req[1].split(":")[1])
            developer.append(detail_req[2].split(":")[1])
            publisher.append(detail_req[3].split(":")[1])
            release.append(detail_req[4].split(":")[1])
            language.append(detail_req[5].split(":")[1])
            file_size.append(detail_req[6].split(":")[1].split("/")[0])
            mirror.append(detail_req[7].split(":")[1])
            req.append(s_req)
            desc_.append(desc)
            panduan_.append(panduan)

            preview_img = [img.attributes["src"] for img in img_ss]
            print(preview_img, file=sys.stderr)

            link__ = {link.text(): link.attributes["href"] for link in link_game}

            if not link__:
                link_games.append(link_op)
            else:
                link_games.append(link__)

            if not preview_img:
                ss_image.append(preview_img_op)
            else:
                ss_image.append(preview_img)

            print(link_games)
            print(ss_image)

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
        except:
            print("gagal")
            break
