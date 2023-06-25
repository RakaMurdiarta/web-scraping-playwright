from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    dataJson = {}
    browser = p.chromium.launch(headless=True, timeout=5000)
    contex = browser.new_context(ignore_https_errors=True, bypass_csp=True)
    page = contex.new_page()
    page.goto("http://nik.depkop.go.id/")
    page.wait_for_load_state("domcontentloaded", timeout=2000)

    provinsi = page.locator('select[id="MainContent_DropDownList1"] option').all()
    total = 0
    for i in range(len(provinsi)):
        provinsi = page.locator('select[id="MainContent_DropDownList1"] option').all()
        p = page.locator("#MainContent_DropDownList1").select_option(value=provinsi[i].get_attribute("value"))
        kab = page.locator('select[id="MainContent_DropDownList2"] option').all()
        for k in range(len(kab)):
            kab = page.locator('select[id="MainContent_DropDownList2"] option').all()
            l = page.locator("#MainContent_DropDownList2").select_option(value=kab[k].get_attribute("value"))
            getText = page.locator("//table[@id='MainContent_DetailsView1']//td[2]")
            if not getText:
                while True:
                    print("get text is empty -- get ulang")
                    getText = page.locator("//table[@id='MainContent_DetailsView1']//td[2]")
                    if getText:
                        break

            sec = getText
            total += int(sec.inner_text())

    print(f"Jumlah Semua Koperasi : ", total)

    f = open("./data-nik/koperasi-uuid.json")
    data_collect = json.load(f)
    len_collect = len(data_collect)

    if total == len_collect:
        print(f"Total data collcet {len_collect} is same as total koperasi {total} [SUCCESS]")
    else:
        print(f"Total data collcet {len_collect} is not same as total koperasi {total} [FAILED]")

    page.close()
