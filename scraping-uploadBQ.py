from concurrent.futures import ThreadPoolExecutor , as_completed
from selectolax.parser import HTMLParser
import requests
import time
import json
import pandas as pd
import pandas_gbq as pg
from google.cloud import bigquery
import warnings
import math
from functools import partial

warnings.filterwarnings("ignore")


def reset_arrays():
    nama_koperasi.clear()
    nik_koperasi.clear()
    badan_hukum.clear()
    tgl_badan_hukum.clear()
    tgl_rat.clear()
    alamat.clear()
    desa.clear()
    kecamatan_koperasi.clear()
    kabupaten_koperasi.clear()
    provinsi_koperasi.clear()
    bentuk_koperasi.clear()
    jenis_koperasi.clear()
    kelompok_koperasi.clear()
    sektor_usaha.clear()
    nama_ketua.clear()
    nama_sektretaris.clear()
    nama_bendahara.clear()
    nama_pengawas.clear()
    jml_pria.clear()
    jml_wanita.clear()
    jml_anggota.clear()
    jml_manajer.clear()
    status_nik.clear()
    tgl_berlaku_serti.clear()
    status_grade.clear()
    jml_karyawan.clear()
    nomor_perubahan_anggaran.clear()
    tgl_perubahan_anggaran.clear()
    nama_manager.clear()


nama_koperasi = []
nik_koperasi = []
badan_hukum = []
tgl_badan_hukum = []
tgl_rat = []
alamat = []
desa = []
kecamatan_koperasi = []
kabupaten_koperasi = []
provinsi_koperasi = []
bentuk_koperasi = []
jenis_koperasi = []
kelompok_koperasi = []
sektor_usaha = []
nama_ketua = []
nama_sektretaris = []
nama_bendahara = []
nama_pengawas = []
nama_manager = []
jml_pria = []
jml_wanita = []
jml_anggota = []
jml_manajer = []
status_nik = []
tgl_berlaku_serti = []
status_grade = []
jml_karyawan = []
nomor_perubahan_anggaran = []
tgl_perubahan_anggaran = []


def Target(element):
    nama_koperasi.append(element[3].text())
    badan_hukum.append(element[5].text())
    tgl_badan_hukum.append(element[7].text())
    nomor_perubahan_anggaran.append(element[9].text())
    tgl_perubahan_anggaran.append(element[11].text())
    tgl_rat.append(element[13].text())
    alamat.append(element[15].text())
    desa.append(element[17].text())
    kecamatan_koperasi.append(element[19].text())
    kabupaten_koperasi.append(element[21].text())
    provinsi_koperasi.append(element[23].text())
    bentuk_koperasi.append(element[25].text())
    jenis_koperasi.append(element[27].text())
    kelompok_koperasi.append(element[29].text())
    sektor_usaha.append(element[31].text())
    nama_ketua.append(element[35].text())
    nama_sektretaris.append(element[37].text())
    nama_bendahara.append(element[39].text())
    nama_pengawas.append(element[41].text())
    nama_manager.append(element[43].text())
    jml_pria.append(element[47].text())
    jml_wanita.append(element[49].text())
    jml_anggota.append(element[51].text())
    jml_manajer.append(element[53].text())
    jml_karyawan.append(element[55].text())
    nik_koperasi.append(element[59].text())
    status_nik.append(element[61].text())
    tgl_berlaku_serti.append(element[63].text())
    status_grade.append(element[65].text())


def process_data(nik):
    try:
        url = f"http://nik.depkop.go.id/Detail.aspx?KoperasiId={nik}"
        resp = requests.get(url)
        html = HTMLParser(resp.text)
        element = html.css("td")
        Target(element)
        return True
    except Exception as e:
        print(f"Error processing NIK: {nik}, Error: {str(e)}")
        return False


def scrape_data(nik_list):
    results = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_data, nik) for nik in nik_list]
        for future in as_completed(futures):
            results.append(future.result())
    return results

def checkingBQ(source_nik):
    batch = 4000
    data_source = [nik_key for nik_key in source_nik.keys()]
    start= 0
    end = 4000
    append_data =[]
    for req__ in range(math.ceil(len(data_source)/batch)):
        print('requst query no :',req__)
        data_slicing= data_source[start:end]
        query = f"""select item from unnest({data_slicing}) as item where item not in (SELECT NIK FROM `dev-sakti.sakti_rnd_dwh.all_koperasi_web_scraping`)"""
        data_BQ = pg.read_gbq(query,project_id='dev-sakti')
        data_ = data_BQ['item']
        nikBQ = data_.to_list()
        print(f'how many data not exist in BQ : {len(nikBQ)}')
        for datanik in nikBQ:
            append_data.append(datanik)
        start +=batch
        end+=batch
    if len(nikBQ)==0:
        return []
        
    return append_data

def checkingStatusKoperasi(list_nik):
    query = f"""SELECT NIK FROM `dev-sakti.sakti_rnd_dwh.all_koperasi_web_scraping` where NIK not in(select item from unnest({list_nik}) as item)"""
    data_BQ = pg.read_gbq(query,project_id='dev-sakti')
    data = data_BQ['NIK'].to_list()
    return data

def updateBQ(nik,client_):
    try:
        query = f"""UPDATE `dev-sakti.sakti_rnd_dwh.all_koperasi_web_scraping` SET Status = "Tidak Aktif" WHERE NIK ={nik}"""
        job = client_.query(query)
        job.result()
        return True
    except Exception as e:
        print(f'there is something wrong this is the error {str(e)}')
        return False


def process_update_BQ(new_nik,client):
    results =[]
    with ThreadPoolExecutor() as executor:
        partial_arg =partial(updateBQ,client)
        futures = [executor.submit(partial_arg , nik_) for nik_ in new_nik]
        for f in futures:
            results.append(f.result())
        return results


df = pd.DataFrame()
clientBQ = bigquery.Client(project='dev-sakti')


open_source_data = open('./data-nik/koperasi_nik.json')
read_source_data = json.load(open_source_data)

#checking nik between source data in BQ
datafromCheckBq = checkingBQ(read_source_data)

if len(datafromCheckBq)==0:
    print('data already up to date')
else:
    #get how many loop needed
    batch_size = 1000
    start_batch = 0
    end_batch=1000
    len_data_current = math.ceil(len(datafromCheckBq)/batch_size)
    for n_data in range(len_data_current):
        start_time = time.time()
        slicing = datafromCheckBq[start_batch : end_batch]
        print("Processing...")
        results = scrape_data(slicing)
        print("End Scraping")
        print('start create df')
        df_concat = pd.DataFrame(
            {
                "Koperasi": nama_koperasi,
                "Nomor_Badan_Hukum_Pendirian": badan_hukum,
                "Tanggal_Badan_Hukum_Pendirian": tgl_badan_hukum,
                "Nomor_Perubahan_Anggaran_Dasar": nomor_perubahan_anggaran,
                "Tanggal_Perubahan_Anggaran_Dasar": tgl_perubahan_anggaran,
                "Tanggal_RAT_Terakhir": tgl_rat,
                "Alamat": alamat,
                "Desa": desa,
                "Kecamatan": kecamatan_koperasi,
                "Kabupaten": kabupaten_koperasi,
                "Provinsi": provinsi_koperasi,
                "Bentuk_Koperasi": bentuk_koperasi,
                "Jenis_Koperasi": jenis_koperasi,
                "Kelompok_Koperasi": kelompok_koperasi,
                "Sektor_Usaha": sektor_usaha,
                "Nama_Ketua": nama_ketua,
                "Nama_Sekretaris": nama_sektretaris,
                "Nama_Bendahara": nama_bendahara,
                "Nama_Pengawas": nama_pengawas,
                "Nama_Manager": nama_manager,
                "Jumlah_Anggota_Pria": jml_pria,
                "Jumlah_Anggota_Wanita": jml_wanita,
                "Total_Anggota": jml_anggota,
                "Total_Manajer": jml_manajer,
                "Total_Karyawan": jml_karyawan,
                "NIK": nik_koperasi,
                "Status_NIK": status_nik,
                "Tanggal_Berlaku_Sertipikat": tgl_berlaku_serti,
                "Status_Grade": status_grade,
                "Status" : "Aktif"
            }
        )

        end_time = time.time()
        execution_time = end_time - start_time

        print("Uploading to BigQuery...")
        client = bigquery.Client(project="dev-sakti")
        dataset_id = "sakti_rnd_dwh"

        dataset_ref = client.dataset(dataset_id)
        job_config = bigquery.LoadJobConfig()
        job_config.autodetect = True
        job_config.write_disposition = "WRITE_APPEND"

        load_job = client.load_table_from_dataframe(
            df_concat, dataset_ref.table("all_koperasi_web_scraping"), job_config=job_config
        )
        df = pd.concat([df_concat, df])
        reset_arrays()
        start_batch+=batch_size
        end_batch+=batch_size
        print(f"DONE LOOP {n_data}")
        print("Execution Time:", execution_time)

        print('prosess checking status koperasi')
        list_koperasi_tidak_aktif = checkingStatusKoperasi(read_source_data)
        process_update_BQ(list_koperasi_tidak_aktif,clientBQ)
        print('proses check done .....')

open_source_data.close()
