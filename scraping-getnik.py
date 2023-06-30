from playwright.sync_api import sync_playwright
import json
import math
import os

folder_path = "./output"


def read_all_json():
    json_files = [file for file in os.listdir(folder_path) if file.endswith(".json")]
    state = {}
    for file in json_files:
        file_path = os.path.join(folder_path, file)
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
            state[file.replace(".json", "").replace("koperasi_nik_", "")] = len(data)
    return state


with sync_playwright() as p:
    state = read_all_json()
    print(state)
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(ignore_https_errors=True, bypass_csp=True)
    page = context.new_page()
    page.goto("http://nik.depkop.go.id/")
    page.wait_for_load_state("domcontentloaded", timeout=2000)
    dropdown_provinsi = page.locator('select[id="MainContent_DropDownList1"] option').all()
    data_provinsi = [text.inner_text() for text in dropdown_provinsi]
    print(data_provinsi)

    for pr in data_provinsi:
        print(pr)
        page.locator("#MainContent_DropDownList1").select_option(pr)
        dropdown_kab = page.locator('select[id="MainContent_DropDownList2"] option').all()
        data_kab = [text.inner_text() for text in dropdown_kab]
        for kabupaten_data in data_kab:
            waitime = 0
            while True:
                try:
                    waitime += 100
                    data = []
                    nik_json = []
                    print(f"Proses data {kabupaten_data}")
                    kabupaten_list = page.locator('select[id="MainContent_DropDownList2"] option').all()
                    page.locator("#MainContent_DropDownList2").select_option(kabupaten_data)
                    getText = page.locator("//table[@id='MainContent_DetailsView1']//td[2]")
                    text = int(getText.inner_text())

                    if kabupaten_data in state:
                        if text == state[kabupaten_data]:
                            print("data already collect go to next kabupaten")
                            break

                    if not text:
                        break
                    print(text)

                    pages_btn = math.ceil(text / 20)
                    print(pages_btn)

                    getatthref = page.locator('//*[@id="MainContent_GridView1"]/tbody/tr/td/a').all()
                    getnik = page.locator('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').all()

                    if not getnik:
                        break
                    if not getatthref:
                        break

                    for nik_data_ in getnik:
                        nik_json.append(nik_data_.inner_text())

                    for d_nik in getatthref:
                        data.append(d_nik.get_attribute(name="href"))

                    for page_kab in range(2, pages_btn + 1):
                        try:
                            print("page kab", page_kab)
                            page.wait_for_selector('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').is_visible()
                            page.click(
                                f"table[id=\"MainContent_GridView1\"] > tbody > tr > td > table > tbody > tr > td > a[href=\"javascript:__doPostBack('ctl00$MainContent$GridView1','Page${page_kab}')\"]"
                            )
                            page.wait_for_timeout(waitime)
                            page.wait_for_selector('//*[@id="MainContent_GridView1"]/tbody/tr/td/a').is_visible()
                            getsecattr = page.locator('//*[@id="MainContent_GridView1"]/tbody/tr/td/a').all()
                            for dx in getsecattr:
                                data.append(dx.get_attribute(name="href"))

                            page.wait_for_selector('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').is_visible()
                            getnik_2 = page.locator('//*[@id="MainContent_GridView1"]/tbody/tr/td[7]').all()

                            for n_i_k in getnik_2:
                                nik_json.append(n_i_k.inner_text())

                        except:
                            print("gagal gether data")
                            break
                    btnHome = page.locator('//*[@id="ctl01"]/div[3]/div/div/ul[1]/li[1]/a')
                    btnHome.click()
                    page.reload()
                    print("ini key", pr)
                    page.locator("#MainContent_DropDownList1").select_option(pr)
                    print(f"nilai text {text} sama dengan panjang data {len(data)}")
                    print(f"nilai text {text} sama dengan panjang nik {len(nik_json)}")

                    if len(data) == text and len(nik_json) == text:
                        result = dict(zip(nik_json, data))
                        with open(f"output/koperasi_nik_{kabupaten_data}.json", "w") as outfile:
                            json.dump(result, outfile)
                        data = []
                        nik_json = []
                        print("process ['SUCCESS]")
                        break
                    print("process ['FAILED] repeat action")

                except:
                    break

    page.close()
    context.close()
    browser.close()
