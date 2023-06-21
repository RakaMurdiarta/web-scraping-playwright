from playwright.sync_api import sync_playwright
import json
import math
import os


jsonData = {}
kabJson = {}
nikJson = {}
validasi = []
validasi_click = []
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("http://nik.depkop.go.id/")
    page.wait_for_load_state("domcontentloaded", timeout=2000)
    dropdown_provinsi = page.locator('select[id="MainContent_DropDownList1"] option').all()
    while True:
        kop = open("./koperasi.json")
        koperasiJson = json.load(kop)
        filteredJson = {}
        for k, v in koperasiJson.items():
            if any(value == "False" for value in v.values()):
                filteredJson[k] = {key: value for key, value in v.items() if value == "False"}

        if len(filteredJson) == 0:
            break

        for key, value in filteredJson.items():
            print(key)
            page.locator("#MainContent_DropDownList1").select_option(key)
            for kabupaten_data in value.keys():
                print(kabupaten_data)
                print("mulai - kab")
                kabupaten_list = page.locator('select[id="MainContent_DropDownList2"] option').all()
                page.locator("#MainContent_DropDownList2").select_option(kabupaten_data)
                page.wait_for_selector('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').is_visible()
                kabupaten_list = page.locator('select[id="MainContent_DropDownList2"] option').all()
                koperasiJson[key][kabupaten_data] = "True"
                jsonData[kabupaten_data] = {}
                page.wait_for_selector('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').is_visible()
                getNikLoop2 = page.locator('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').all()
                for nik2 in range(len(getNikLoop2)):
                    niktext = getNikLoop2[nik2]
                    validasi.append(niktext.inner_text())
                lengthPage = page.locator("//table[@id='MainContent_DetailsView1']//td[2]")
                if (len(validasi) == 20) or (len(validasi) == int(lengthPage.inner_text())):
                    print("masuk valid")
                    getNikLoop2 = page.locator('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').all()
                    for nik2 in range(len(getNikLoop2)):
                        niktext = getNikLoop2[nik2]
                        nikJson[niktext.inner_text()] = "False"
                        jsonData[kabupaten_data][niktext.inner_text()] = "False"
                else:
                    print("masuk while")
                    while True:
                        validasi.clear()
                        getNikLoop2 = page.locator('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').all()
                        for nik2 in range(len(getNikLoop2)):
                            getNikLoop2 = page.locator('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').all()
                            niktext = getNikLoop2[nik2]
                            validasi.append(niktext.inner_text())
                        if len(validasi) == 20:
                            for nik2 in range(len(getNikLoop2)):
                                getNikLoop2 = page.locator('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').all()
                                niktext = getNikLoop2[nik2]
                                print(niktext.inner_text())
                                nikJson[niktext.inner_text()] = "False"
                                jsonData[kabupaten_data][niktext.inner_text()] = "False"
                            break
                lengthPage = page.locator("//table[@id='MainContent_DetailsView1']//td[2]")
                print("Total Pages", math.ceil(int(lengthPage.inner_text()) / 20))
                lengthPage = page.locator("//table[@id='MainContent_DetailsView1']//td[2]")
                for pagesLength in range(2, math.ceil(int(lengthPage.inner_text()) / 20) + 1):
                    page.click(
                        f"table[id=\"MainContent_GridView1\"] > tbody > tr > td > table > tbody > tr > td > a[href=\"javascript:__doPostBack('ctl00$MainContent$GridView1','Page${pagesLength}')\"]"
                    )
                    page.wait_for_selector('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').is_visible()
                    getNikLoop3 = page.locator('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').all()
                    for nikw in range(len(getNikLoop3)):
                        # getNikLoop3 = page.locator('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').all()
                        nik2text = getNikLoop3[nikw]
                        validasi_click.append(nik2text.inner_text())
                lengthPage = page.locator("//table[@id='MainContent_DetailsView1']//td[2]")
                print("validasi click", len(validasi_click))
                if len(validasi_click) == int(lengthPage.inner_text()) - 20:
                    print("masuk validasi valid 2 btn click")
                    getNikLoop3 = page.locator('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').all()
                    for valid_ in validasi_click:
                        nikJson[valid_] = "False"
                        jsonData[kabupaten_data][valid_] = "False"
                    with open(f"data_kabupaten/koperasi_nik_{kabupaten_data}.json", "w") as outfile:
                        json.dump(nikJson, outfile)

                    with open(f"data_kabupaten/data-json-{kabupaten_data}.json", "w") as jsonWrite:
                        json.dump(jsonData, jsonWrite)
                    validasi_click.clear()
                    validasi.clear()
                elif len(validasi) == int(lengthPage.inner_text()):
                    print("masuk elif validasi ")
                    with open(f"data_kabupaten/koperasi_nik_{kabupaten_data}.json", "w") as outfile:
                        json.dump(nikJson, outfile)

                    with open(f"data_kabupaten/data-json-{kabupaten_data}.json", "w") as jsonWrite:
                        json.dump(jsonData, jsonWrite)
                    validasi_click.clear()
                    validasi.clear()
                else:
                    print("masuk while validasi 2 btn click")
                    validasi_click.clear()
                    while True:
                        btnHome = page.locator('//*[@id="ctl01"]/div[3]/div/div/ul[1]/li[1]/a')
                        btnHome.click()
                        page.reload()
                        print("in yaa", key)
                        page.locator("#MainContent_DropDownList1").select_option(key)
                        page.locator("#MainContent_DropDownList2").select_option(kabupaten_data)
                        lengthPage = page.locator("//table[@id='MainContent_DetailsView1']//td[2]")
                        for pagesLength in range(2, math.ceil(int(lengthPage.inner_text()) / 20) + 1):
                            page.click(
                                f"table[id=\"MainContent_GridView1\"] > tbody > tr > td > table > tbody > tr > td > a[href=\"javascript:__doPostBack('ctl00$MainContent$GridView1','Page${pagesLength}')\"]"
                            )
                            page.wait_for_selector('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').is_visible()
                            getNikLoop3 = page.locator('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').all()
                            for nikw in range(len(getNikLoop3)):
                                getNikLoop3 = page.locator('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').all()
                                nik2text = getNikLoop3[nikw]
                                validasi_click.append(nik2text.inner_text())

                        if len(validasi_click) == int(lengthPage.inner_text()) - 20:
                            print("validdd while")
                            getNikLoop3 = page.locator('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').all()
                            for valid_ in validasi_click:
                                nikJson[valid_] = "False"
                                jsonData[kabupaten_data][valid_] = "False"
                            with open(f"data_kabupaten/koperasi_nik_{kabupaten_data}.json", "w") as outfile:
                                json.dump(nikJson, outfile)

                            with open(f"data_kabupaten/data-json-{kabupaten_data}.json", "w") as jsonWrite:
                                json.dump(jsonData, jsonWrite)
                            validasi_click.clear()
                            validasi.clear()
                            break
                with open("./koperasi.json", "w") as outputxx:
                    json.dump(koperasiJson, outputxx)
                btnHome = page.locator('//*[@id="ctl01"]/div[3]/div/div/ul[1]/li[1]/a')
                btnHome.click()
                # page.click('//*[@id="ctl01"]/div[3]/div/div/ul[1]/li[1]/a')
                page.reload()
                # wait = page.wait_for_selector('select[id="MainContent_DropDownList1"]', timeout=5000, state="attached")
                print("ini key", key)
                # wait = page.wait_for_selector('select[id="MainContent_DropDownList1"]', timeout=5000)
                page.locator("#MainContent_DropDownList1").select_option(key)
                # page.wait_for_load_state("domcontentloaded", timeout=2000)
            print("click home provinsi")
        # print(json.dumps(nikJson, indent=2))
        with open("data/koperasi_nik_full.json", "w") as outfile:
            json.dump(nikJson, outfile)

        with open("data/data-json-full.json", "w") as jsonWrite:
            json.dump(jsonData, jsonWrite)
    page.close()
os.system("shutdown -s")
