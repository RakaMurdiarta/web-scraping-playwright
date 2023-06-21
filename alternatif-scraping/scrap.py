from playwright.sync_api import sync_playwright
import json
import math
import time
import os

jsonData = {}
kabJson = {}
list_nik = {}

start = time.time()
folder_path = './alljson'  # Replace with the path to your folder

def getDom(page, locator):
    wait = page.wait_for_selector('select[id="MainContent_DropDownList1"]', timeout=8000, state="attached")
    if wait:
        dom = page.query_selector_all(locator)
        return dom

def read_all_json():
    json_files = [file for file in os.listdir(folder_path) if file.endswith('.json')]
    state = {}
    for file in json_files:
        file_path = os.path.join(folder_path, file)
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            state[file.replace(".json","").replace("nik_","")] = len(data)
    return state

with sync_playwright() as p:
    state = read_all_json()
    browser = p.chromium.launch(headless=True,devtools=True)
    page = browser.new_page()
    page.route("**/*twk*.js", lambda route: route.abort()) 
    page.route('**/twk-main.js', lambda route: route.abort())
    page.goto("http://nik.depkop.go.id/")
    page.wait_for_load_state("domcontentloaded", timeout=2000)
    dropdown_provinsi = getDom(page, 'select[id="MainContent_DropDownList1"] option')
    list_provinsi = [x.inner_text() for x in dropdown_provinsi]
    # list_provinsi = [list_provinsi[0]]
    for provinsi in list_provinsi:
        print(provinsi)
        page.locator("#MainContent_DropDownList1").select_option(label=provinsi)
        page.wait_for_selector(selector='select[id="MainContent_DropDownList2"]', timeout=2000)
        dropdown_kabupaten = getDom(page, 'select[id="MainContent_DropDownList2"] option')
        list_kabupaten = [x.inner_text() for x in dropdown_kabupaten]
        # list_kabupaten = list_kabupaten[3:5]
        for kabupaten in list_kabupaten:
            waittime = 0
            while True:
                try:
                    print(waittime)
                    waittime += 100
                    page.route("**/*twk*.js", lambda route: route.abort()) 
                    page.goto("http://nik.depkop.go.id/")
                    page.locator("#MainContent_DropDownList1").select_option(label=provinsi)
                    page.locator("#MainContent_DropDownList2").select_option(label=kabupaten)
                    page.wait_for_selector('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').is_visible()
                    item_count = int(page.locator('//*[@id="MainContent_DetailsView1"]/tbody/tr/td[2]').inner_text())

                    if(kabupaten in state):
                        if(item_count == state[kabupaten]):
                            print(f"{kabupaten} already gathered")
                            break

                    # each page has 20 items
                    length_pages = math.ceil(item_count / 20)
                    temp_nik = []
                    check_count = item_count
                    for pages in range(1,length_pages + 1):
                        page.wait_for_selector('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]')
                        try:
                            page.evaluate('document.querySelector(".widget-visible").className = "widget-hide"')
                        except:
                            pass
                        page.wait_for_load_state("domcontentloaded", timeout=2000)
                        page.wait_for_selector('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').is_visible()
                        page.wait_for_timeout(waittime)
                        try:
                            nik = page.locator('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').all_inner_texts()
                        except:
                            print("error getting data")
                            break
                        print(length_pages,pages,len(nik))
                        temp_nik.extend(nik)
                        if(pages + 1 < length_pages + 1):
                            page.wait_for_load_state("domcontentloaded", timeout=2000)
                            try:
                                wait = page.wait_for_selector('select[id="MainContent_DropDownList1"]', timeout=5000, state="attached")
                                page.wait_for_selector('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').is_visible()
                                # page.evaluate(f"""__doPostBack('ctl00$MainContent$GridView1','Page${pages+1}')""")
                                page.click(
                                    f"table[id=\"MainContent_GridView1\"] > tbody > tr > td > table > tbody > tr > td > a[href=\"javascript:__doPostBack('ctl00$MainContent$GridView1','Page${pages+1}')\"]",
                                    timeout=1000
                                )
                            except:
                                print("error goto next page")
                                break
                            page.wait_for_load_state("domcontentloaded", timeout=2000)
                    temp_nik = set(temp_nik)
                    print(f'{kabupaten} has {item_count} koperasi, success getting {len(temp_nik)}.',end='')
                    if(item_count == len(temp_nik)):
                        temp_nik = {x : False for x in temp_nik}
                        # list_nik.update(temp_nik)
                        print(' [Done]')
                        file_path = os.path.join(folder_path, f"nik_{kabupaten}.json")
                        with open(file_path, "w") as outfile:
                            json.dump(temp_nik, outfile)
                        break
                    else:
                        print(' [Fail].')
                except:
                    print('Retry.')
    page.close()

print(time.time() - start)