import asyncio
import os
from html.parser import HTMLParser

import requests

import wget
from bs4 import BeautifulSoup
from sample_config import Config
from uniborg.util import admin_cmd


@borg.on(admin_cmd(pattern=("coronatr ?(.*)"))) # pylint:disable=E0602
async def cor_tr(event):
    x = await event.edit("`Corona Virüs Bilgileri https://covid19.saglik.gov.tr/ adresinden alınıyor..`")
    try:
        r = requests.get("https://covid19.saglik.gov.tr/")
        if r.status_code == 200:
            sayfa_linki = requests.get('https://covid19.saglik.gov.tr/')
            soup =  BeautifulSoup(sayfa_linki.content, 'html.parser')
            vakalar = soup.find_all(class_="list-group list-group-genislik")
            vaka = vakalar[0].text.split()
            toplam_test = vaka[3]
            toplam_vaka = vaka[7]
            toplam_olum = vaka[11]
            toplam_yog_bakım = vaka[17]
            entube = vaka[22]
            iyilesen = vaka[27]


            bugun_test = soup.find(class_="buyuk-bilgi-l-sayi").text
            bugun_= soup.find_all("span",class_="")
            bugun_vaka = bugun_[13].text
            bugun_vefat = bugun_[15].text
            bugun_iyilesen = bugun_[17].text

            msg = """
Sağlık Bakanlığı Corona Virus Bilgileri
Kaynak: `https://covid19.saglik.gov.tr/`

Toplam Test: **{}**
Toplam Vaka: **{}**
Toplam Vefat: **{}**
Toplam Yoğun Bakımdaki Hasta: **{}**
Toplam Entübe: **{}**
Toplam İyileşen: **{}**

Bugünün Verileri

Bugünkü Test: **{}**
Bugünkü Vaka: **{}**
Bugünkü Vefat: **{}**
Bugünkü İyileşen: **{}**
""".format(
    toplam_test,
    toplam_vaka,
    toplam_olum,
    toplam_yog_bakım,
    entube,iyilesen,
    bugun_test,
    bugun_vaka,
    bugun_vefat,
    bugun_iyilesen
)
            await x.edit(msg)
        else:
            await x.edit("`Bakanlık sitesine bağlanırken sorun oluştu`")
    except HTMLParser.HTMLParseError as err:
        await x.edit("`Hata oluştu. Hata kodu: {}`".format(str(err)))
