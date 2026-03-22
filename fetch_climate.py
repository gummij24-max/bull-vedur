"""
Sækir ársmeðaltöl frá Veðurstofu Íslands fyrir allar 195 veðurstöðvar
og vistar niðurstöðuna í static/climate_averages.json

Keyra: python3 fetch_climate.py
"""

import json
import time
import urllib.request
from statistics import mean

STATIONS = [
  {"id": 1,   "name": "Reykjavík",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_001_Reykjavik.ArsMedal.txt"},
  {"id": 10,  "name": "Vídistöðir",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_010_Vidistadir.ArsMedal.txt"},
  {"id": 12,  "name": "Straumsvík",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_012_Straumsvik.ArsMedal.txt"},
  {"id": 15,  "name": "Vífílsstöðir",                   "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_015_Vifilsstadir.ArsMedal.txt"},
  {"id": 20,  "name": "Ellidáarstöð",                   "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_020_Ellidaarstod.ArsMedal.txt"},
  {"id": 25,  "name": "Rjúpnahæð",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_025_Rjupnahad.ArsMedal.txt"},
  {"id": 30,  "name": "Hólmur",                         "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_030_Holmur.ArsMedal.txt"},
  {"id": 46,  "name": "Korpa",                          "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_046_Korpa.ArsMedal.txt"},
  {"id": 51,  "name": "Mosfell",                        "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_051_Mosfell.ArsMedal.txt"},
  {"id": 68,  "name": "Stíflisdalur",                   "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_068_Stiflisdalur.ArsMedal.txt"},
  {"id": 70,  "name": "Stardalur",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_070_Stardalur.ArsMedal.txt"},
  {"id": 73,  "name": "Mógílsá",                        "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_073_Mogilsa.ArsMedal.txt"},
  {"id": 83,  "name": "Meðalfell",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_083_Medalfell.ArsMedal.txt"},
  {"id": 88,  "name": "Stóri-Botn",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_088_Stori_Botn.ArsMedal.txt"},
  {"id": 93,  "name": "Grundartangi",                   "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_093_Grundartangi.ArsMedal.txt"},
  {"id": 94,  "name": "Kirkjubøl",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_094_Kirkjubol.ArsMedal.txt"},
  {"id": 95,  "name": "Akranes",                        "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_095_Akranes.ArsMedal.txt"},
  {"id": 97,  "name": "Neðra-Skörð",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_097_Nedra_Skard.ArsMedal.txt"},
  {"id": 103, "name": "Andakílsárvirkjun",              "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_103_Andakilsarvirkjun.ArsMedal.txt"},
  {"id": 105, "name": "Hvaneyri",                       "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_105_Hvanneyri.ArsMedal.txt"},
  {"id": 108, "name": "Stafholtsey",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_108_Stafholtsey.ArsMedal.txt"},
  {"id": 117, "name": "Augastöðir",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_117_Augastadir.ArsMedal.txt"},
  {"id": 120, "name": "Kalmanstunga",                   "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_120_Kalmanstunga.ArsMedal.txt"},
  {"id": 126, "name": "Síðumúli",                       "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_126_Sidumuli.ArsMedal.txt"},
  {"id": 132, "name": "Brekka",                         "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_132_Brekka.ArsMedal.txt"},
  {"id": 136, "name": "Fornihvammur",                   "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_136_Fornihvammur.ArsMedal.txt"},
  {"id": 145, "name": "Tverholt",                       "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_145_Tverholt.ArsMedal.txt"},
  {"id": 149, "name": "Hítardalur",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_149_Hitardalur.ArsMedal.txt"},
  {"id": 163, "name": "Hjardárfell",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_163_Hjardarfell.ArsMedal.txt"},
  {"id": 166, "name": "Búðvarsholt",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_166_Bodvarsholt.ArsMedal.txt"},
  {"id": 167, "name": "Blafeldur",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_167_Blafeldur.ArsMedal.txt"},
  {"id": 168, "name": "Arnarstapi",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_168_Arnarstapi.ArsMedal.txt"},
  {"id": 170, "name": "Gufuskálar",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_170_Gufuskalar.ArsMedal.txt"},
  {"id": 171, "name": "Hellissandur",                   "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_171_Hellissandur.ArsMedal.txt"},
  {"id": 177, "name": "Setberg",                        "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_177_Setberg.ArsMedal.txt"},
  {"id": 178, "name": "Stykkishólmur",                  "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_178_Stykkisholmur.ArsMedal.txt"},
  {"id": 187, "name": "Kvennabrekka",                   "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_187_Kvennabrekka.ArsMedal.txt"},
  {"id": 188, "name": "Hamraendar",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_188_Hamraendar.ArsMedal.txt"},
  {"id": 192, "name": "Búðardalur",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_192_Budardalur.ArsMedal.txt"},
  {"id": 195, "name": "Ásgarður",                       "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_195_Asgardur.ArsMedal.txt"},
  {"id": 202, "name": "Máskelda",                       "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_202_Maskelda.ArsMedal.txt"},
  {"id": 203, "name": "Mýrartunga II",                  "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_203_Myrartunga_II.ArsMedal.txt"},
  {"id": 206, "name": "Reykihólar",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_206_Reykholar.ArsMedal.txt"},
  {"id": 210, "name": "Flatey",                         "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_210_Flatey.ArsMedal.txt"},
  {"id": 212, "name": "Brjánslækur",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_212_Brjanslakur.ArsMedal.txt"},
  {"id": 220, "name": "Lambavatn",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_220_Lambavatn.ArsMedal.txt"},
  {"id": 221, "name": "Hánuvík",                        "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_221_Hanuvik.ArsMedal.txt"},
  {"id": 222, "name": "Hvallatur",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_222_Hvallatur.ArsMedal.txt"},
  {"id": 224, "name": "Kvígindisdalur",                 "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_224_Kvigindisdalur.ArsMedal.txt"},
  {"id": 231, "name": "Mjólkárvirkjun",                 "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_231_Mjolkarvirkjun.ArsMedal.txt"},
  {"id": 234, "name": "Hólar í Dýrafirði",              "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_234_Holar_i_Dyrafirdi.ArsMedal.txt"},
  {"id": 240, "name": "Þórusstöðir",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_240_Torustadir.ArsMedal.txt"},
  {"id": 241, "name": "Vaðlar",                         "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_241_Vadlar.ArsMedal.txt"},
  {"id": 244, "name": "Flateyri",                       "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_244_Flateyri.ArsMedal.txt"},
  {"id": 247, "name": "Birkihlíð í Súgandafirði",       "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_247_Birkihlid_i_Sugandafirdi.ArsMedal.txt"},
  {"id": 248, "name": "Suðureyri",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_248_Sudureyri.ArsMedal.txt"},
  {"id": 250, "name": "Galtarviti",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_250_Galtarviti.ArsMedal.txt"},
  {"id": 252, "name": "Bölungarvik",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_252_Bolungarvik.ArsMedal.txt"},
  {"id": 253, "name": "Hnífsdal",                       "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_253_Hnifsdalur.ArsMedal.txt"},
  {"id": 254, "name": "Ísafjörður",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_254_Isafjordur.ArsMedal.txt"},
  {"id": 258, "name": "Hrafnabjörg",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_258_Hrafnabjorg.ArsMedal.txt"},
  {"id": 260, "name": "Áðey",                           "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_260_Adey.ArsMedal.txt"},
  {"id": 285, "name": "Hornbjargsviti",                 "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_285_Hornbjargsviti.ArsMedal.txt"},
  {"id": 291, "name": "Munadalornes",                   "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_291_Munadarnes.ArsMedal.txt"},
  {"id": 293, "name": "Litla-Ávík",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_293_Litla_Avik.ArsMedal.txt"},
  {"id": 295, "name": "Gjögur",                         "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_295_Gjogur.ArsMedal.txt"},
  {"id": 296, "name": "Bassastöðir",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_296_Bassastadir.ArsMedal.txt"},
  {"id": 300, "name": "Steinadalur",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_300_Steinadalur.ArsMedal.txt"},
  {"id": 303, "name": "Hlaðhammar",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_303_Hladhamar.ArsMedal.txt"},
  {"id": 309, "name": "Þóroddsstöðir",                  "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_309_Toroddsstadir.ArsMedal.txt"},
  {"id": 310, "name": "Tanstöðabakki",                  "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_310_Tannstadabakki.ArsMedal.txt"},
  {"id": 311, "name": "Reykir í Hrútafirði",            "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_311_Reykir_i_Hrutafirdi.ArsMedal.txt"},
  {"id": 315, "name": "Barkarstöðir",                   "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_315_Barkarstadir.ArsMedal.txt"},
  {"id": 321, "name": "Ásbjarnarstöðir",                "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_321_Asbjarnarstadir.ArsMedal.txt"},
  {"id": 333, "name": "Brúsastöðir",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_333_Brusastadir.ArsMedal.txt"},
  {"id": 335, "name": "Forsáludalur",                   "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_335_Forsaludalur.ArsMedal.txt"},
  {"id": 340, "name": "Hjaltabakki",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_340_Hjaltabakki.ArsMedal.txt"},
  {"id": 341, "name": "Blönduós",                       "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_341_Blonduos.ArsMedal.txt"},
  {"id": 346, "name": "Stafn",                          "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_346_Stafn.ArsMedal.txt"},
  {"id": 352, "name": "Hraun á Skaga",                  "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_352_Hraun_a_Skaga.ArsMedal.txt"},
  {"id": 360, "name": "Sauðárkrókur",                   "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_360_Saudarkrokur.ArsMedal.txt"},
  {"id": 361, "name": "Bergstöðir",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_361_Bergstadir.ArsMedal.txt"},
  {"id": 366, "name": "Nautabú",                        "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_366_Nautabu.ArsMedal.txt"},
  {"id": 370, "name": "Litla-Hlíð",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_370_Litla_Hlid.ArsMedal.txt"},
  {"id": 383, "name": "Dalsmynni",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_383_Dalsmynni.ArsMedal.txt"},
  {"id": 385, "name": "Hólar í Hjaltadal",              "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_385_Holar_i_Hjaltadal.ArsMedal.txt"},
  {"id": 396, "name": "Skeiðsfoss",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_396_Skeidsfoss.ArsMedal.txt"},
  {"id": 400, "name": "Sauðánesviti",                   "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_400_Saudanesviti.ArsMedal.txt"},
  {"id": 401, "name": "Siglufjörður",                   "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_401_Siglufjordur.ArsMedal.txt"},
  {"id": 402, "name": "Siglunes",                       "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_402_Siglunes.ArsMedal.txt"},
  {"id": 404, "name": "Grímsey",                        "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_404_Grimsey.ArsMedal.txt"},
  {"id": 406, "name": "Kálfságrkot",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_406_Kalfsarkot.ArsMedal.txt"},
  {"id": 409, "name": "Tjörn",                          "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_409_Tjorn.ArsMedal.txt"},
  {"id": 412, "name": "Hrísey",                         "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_412_Hrisey.ArsMedal.txt"},
  {"id": 420, "name": "Audnir",                         "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_420_Audnir.ArsMedal.txt"},
  {"id": 422, "name": "Akureyri",                       "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_422_Akureyri.ArsMedal.txt"},
  {"id": 425, "name": "Torfur",                         "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_425_Torfur.ArsMedal.txt"},
  {"id": 426, "name": "Torfufell",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_426_Torfufell.ArsMedal.txt"},
  {"id": 427, "name": "Gullbrekka",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_427_Gullbrekka.ArsMedal.txt"},
  {"id": 437, "name": "Þverá í Dalsmynni",              "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_437_Tvera_i_Dalsmynni.ArsMedal.txt"},
  {"id": 445, "name": "Sólvangur",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_445_Solvangur.ArsMedal.txt"},
  {"id": 447, "name": "Vaglir II",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_447_Vaglir_II.ArsMedal.txt"},
  {"id": 448, "name": "Lerkihlíð",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_448_Lerkihlid.ArsMedal.txt"},
  {"id": 452, "name": "Sandur",                         "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_452_Sandur.ArsMedal.txt"},
  {"id": 458, "name": "Sandhaugar",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_458_Sandhaugar.ArsMedal.txt"},
  {"id": 462, "name": "Mýri",                           "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_462_Myri.ArsMedal.txt"},
  {"id": 463, "name": "Svartárkot",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_463_Svartarkot.ArsMedal.txt"},
  {"id": 465, "name": "Haganes",                        "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_465_Haganes.ArsMedal.txt"},
  {"id": 468, "name": "Reykjahlíð",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_468_Reykjahlid.ArsMedal.txt"},
  {"id": 473, "name": "Stadárhöll",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_473_Stadarholl.ArsMedal.txt"},
  {"id": 476, "name": "Skógargerði",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_476_Skogargerdi.ArsMedal.txt"},
  {"id": 477, "name": "Húsavík",                        "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_477_Husavik.ArsMedal.txt"},
  {"id": 479, "name": "Márarbakki",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_479_Manarbakki.ArsMedal.txt"},
  {"id": 484, "name": "Garður",                         "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_484_Gardur.ArsMedal.txt"},
  {"id": 490, "name": "Móðrudalur",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_490_Modrudalur.ArsMedal.txt"},
  {"id": 495, "name": "Grímsstöðir",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_495_Grimsstadir.ArsMedal.txt"},
  {"id": 502, "name": "Raufarféhn",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_502_Raufarhofn.ArsMedal.txt"},
  {"id": 503, "name": "Sigurðarstöðir",                 "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_503_Sigurdarstadir.ArsMedal.txt"},
  {"id": 504, "name": "Höskuldaðarnes",                 "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_504_Hoskuldarnes.ArsMedal.txt"},
  {"id": 505, "name": "Raufarhöfn",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_505_Raufarhofn.ArsMedal.txt"},
  {"id": 508, "name": "Sauðanes",                       "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_508_Saudanes.ArsMedal.txt"},
  {"id": 510, "name": "Skóruvik",                       "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_510_Skoruvik.ArsMedal.txt"},
  {"id": 515, "name": "Miðfjardárnes",                  "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_515_Midfjardarnes.ArsMedal.txt"},
  {"id": 519, "name": "Þorvaldsstaðir",                 "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_519_Torvaldsstadir.ArsMedal.txt"},
  {"id": 521, "name": "Strandhöfn",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_521_Strandhofn.ArsMedal.txt"},
  {"id": 525, "name": "Vopnafjörður",                   "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_525_Vopnafjordur.ArsMedal.txt"},
  {"id": 527, "name": "Skjaldtingsstöðir",              "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_527_Skjaldtingsstadir.ArsMedal.txt"},
  {"id": 533, "name": "Fagridalur",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_533_Fagridalur.ArsMedal.txt"},
  {"id": 542, "name": "Brú á Jökuldalí",                "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_542_Bru_a_Jokuldal_I.ArsMedal.txt"},
  {"id": 562, "name": "Dratthálastöðir",                "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_562_Dratthalastadir.ArsMedal.txt"},
  {"id": 565, "name": "Svinafell",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_565_Svinafell.ArsMedal.txt"},
  {"id": 570, "name": "Egilsstöðir",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_570_Egilsstadir.ArsMedal.txt"},
  {"id": 575, "name": "Grímsárvirkjun",                 "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_575_Grimsarvirkjun.ArsMedal.txt"},
  {"id": 578, "name": "Birkihlíð",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_578_Birkihlid.ArsMedal.txt"},
  {"id": 580, "name": "Hallormsstöðuhur",                "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_580_Hallormsstadur.ArsMedal.txt"},
  {"id": 590, "name": "Skriðuklaustur",                 "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_590_Skriduklaustur.ArsMedal.txt"},
  {"id": 607, "name": "Hvannstöð",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_607_Hvannstod.ArsMedal.txt"},
  {"id": 608, "name": "Desjarmýri",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_608_Desjarmyri.ArsMedal.txt"},
  {"id": 615, "name": "Seyðisfjörður",                  "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_615_Seydisfjordur.ArsMedal.txt"},
  {"id": 616, "name": "Hánefsstaðir",                   "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_616_Hanefsstadir.ArsMedal.txt"},
  {"id": 620, "name": "Dalatangi",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_620_Dalatangi.ArsMedal.txt"},
  {"id": 625, "name": "Neskaupstaður veðurfarssstöð",   "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_625_Neskaupstadur_vedurfarsstod.ArsMedal.txt"},
  {"id": 626, "name": "Neskaupstaður",                  "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_626_Neskaupstadur.ArsMedal.txt"},
  {"id": 635, "name": "Kollaleira",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_635_Kollaleira.ArsMedal.txt"},
  {"id": 660, "name": "Kambanes",                       "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_660_Kambanes.ArsMedal.txt"},
  {"id": 666, "name": "Gílsá",                          "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_666_Gilsa.ArsMedal.txt"},
  {"id": 670, "name": "Núpur",                          "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_670_Nupur.ArsMedal.txt"},
  {"id": 675, "name": "Teigarhorn",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_675_Teigarhorn.ArsMedal.txt"},
  {"id": 676, "name": "Djúpivogur",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_676_Djupivogur.ArsMedal.txt"},
  {"id": 694, "name": "Stafafell",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_694_Stafafell.ArsMedal.txt"},
  {"id": 705, "name": "Höfn í Hornafirði",              "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_705_Hofn_i_Hornafirdi.ArsMedal.txt"},
  {"id": 706, "name": "Hjardárnes",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_706_Hjardarnes.ArsMedal.txt"},
  {"id": 707, "name": "Akurnes",                        "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_707_Akurnes.ArsMedal.txt"},
  {"id": 709, "name": "Borgir í Hornafirði",            "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_709_Borgir_i_Hornafirdi.ArsMedal.txt"},
  {"id": 710, "name": "Hólar í Hornafirði",             "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_710_Holar_i_Hornafirdi.ArsMedal.txt"},
  {"id": 735, "name": "Vagnsstaðir",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_735_Vagnsstadir.ArsMedal.txt"},
  {"id": 738, "name": "Hali",                           "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_738_Hali.ArsMedal.txt"},
  {"id": 740, "name": "Kvisker",                        "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_740_Kvisker.ArsMedal.txt"},
  {"id": 745, "name": "Fagurholsmýri",                  "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_745_Fagurholsmyri.ArsMedal.txt"},
  {"id": 748, "name": "Skaftafell",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_748_Skaftafell.ArsMedal.txt"},
  {"id": 768, "name": "Dalshöfði",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_768_Dalshofdi.ArsMedal.txt"},
  {"id": 772, "name": "Kirkjubæjarklaustur",            "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_772_Kirkjubajarklaustur.ArsMedal.txt"},
  {"id": 784, "name": "Snábýli",                        "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_784_Snabyli.ArsMedal.txt"},
  {"id": 790, "name": "Mýrar í Álftaveri",              "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_790_Myrar_i_Alftaveri.ArsMedal.txt"},
  {"id": 791, "name": "Norðurhjáleiga",                 "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_791_Nordurhjaleiga.ArsMedal.txt"},
  {"id": 796, "name": "Kerlingardalur",                 "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_796_Kerlingardalur.ArsMedal.txt"},
  {"id": 798, "name": "Vík í Mýrdal",                   "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_798_Vik_i_Myrdal.ArsMedal.txt"},
  {"id": 802, "name": "Vatnsskarðshólar",               "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_802_Vatnsskardsholar.ArsMedal.txt"},
  {"id": 806, "name": "Drangshlíðardalur",              "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_806_Drangshlidardalur.ArsMedal.txt"},
  {"id": 807, "name": "Skógár",                         "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_807_Skogar.ArsMedal.txt"},
  {"id": 815, "name": "Stórthöfði",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_815_Storhofdi.ArsMedal.txt"},
  {"id": 816, "name": "Vestmannaeyjabar",               "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_816_Vestmannaeyjabar.ArsMedal.txt"},
  {"id": 818, "name": "Hólmar",                         "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_818_Holmar.ArsMedal.txt"},
  {"id": 821, "name": "Bergtórshvoll",                  "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_821_Bergtorshvoll.ArsMedal.txt"},
  {"id": 824, "name": "Búð í Tykkvabæ",                 "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_824_Bud_i_Tykkvaba.ArsMedal.txt"},
  {"id": 825, "name": "Onnupartur",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_825_Onnupartur.ArsMedal.txt"},
  {"id": 827, "name": "Bjóla í Tykkvabæ",              "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_827_Bjola_i_Tykkvaba.ArsMedal.txt"},
  {"id": 832, "name": "Kornvellir",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_832_Kornvellir.ArsMedal.txt"},
  {"id": 846, "name": "Samsstaðir",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_846_Samsstadir.ArsMedal.txt"},
  {"id": 855, "name": "Hella",                          "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_855_Hella.ArsMedal.txt"},
  {"id": 875, "name": "Leirubakki",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_875_Leirubakki.ArsMedal.txt"},
  {"id": 892, "name": "Hveravellir",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_892_Hveravellir.ArsMedal.txt"},
  {"id": 899, "name": "Búrfell",                        "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_899_Burfell.ArsMedal.txt"},
  {"id": 902, "name": "Járar",                          "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_902_Jadar.ArsMedal.txt"},
  {"id": 907, "name": "Hall",                           "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_907_Hall.ArsMedal.txt"},
  {"id": 910, "name": "Blesastöðir",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_910_Blesastadir.ArsMedal.txt"},
  {"id": 915, "name": "Forseti",                        "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_915_Forsati.ArsMedal.txt"},
  {"id": 919, "name": "Lækjarbakki",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_919_Lakjarbakki.ArsMedal.txt"},
  {"id": 923, "name": "Eyrarbakki",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_923_Eyrarbakki.ArsMedal.txt"},
  {"id": 927, "name": "Laugardálir",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_927_Laugardalir.ArsMedal.txt"},
  {"id": 931, "name": "Hjardárland",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_931_Hjardarland.ArsMedal.txt"},
  {"id": 932, "name": "Vegatunga",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_932_Vegatunga.ArsMedal.txt"},
  {"id": 936, "name": "Austurey II",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_936_Austurey_II.ArsMedal.txt"},
  {"id": 938, "name": "Miðfell",                        "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_938_Midfell.ArsMedal.txt"},
  {"id": 945, "name": "Þingvellir",                     "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_945_Tingvellir.ArsMedal.txt"},
  {"id": 949, "name": "Heiðarbær",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_949_Heidarbar.ArsMedal.txt"},
  {"id": 951, "name": "Nesjavellir",                    "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_951_Nesjavellir.ArsMedal.txt"},
  {"id": 955, "name": "Ljósafoss",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_955_Ljosafoss.ArsMedal.txt"},
  {"id": 956, "name": "Írafoss",                        "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_956_Irafoss.ArsMedal.txt"},
  {"id": 957, "name": "Reykir í Ölfusi",                "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_957_Reykir_i_Olfusi.ArsMedal.txt"},
  {"id": 971, "name": "Vogsósar",                       "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_971_Vogsosar.ArsMedal.txt"},
  {"id": 983, "name": "Grindavík",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_983_Grindavik.ArsMedal.txt"},
  {"id": 985, "name": "Reykjanes",                      "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_985_Reykjanes.ArsMedal.txt"},
  {"id": 990, "name": "Keflavíkurflugvöllur",           "url": "http://www.vedur.is/Medaltalstoflur-txt/Stod_990_Keflavikurflugvollur.ArsMedal.txt"},
]

# Column indices in each data row (0-based after stripping leading whitespace)
# stöð ár t tx txx txxD1 tn tnn tnnD1 rh r rx rxD1 p n sun f
COL_AR  = 1   # year
COL_T   = 2   # mean temp
COL_TX  = 3   # mean daily max
COL_TN  = 6   # mean daily min
COL_R   = 10  # annual precip (mm)
COL_F   = 16  # mean wind (m/s)

MIN_YEARS_PREFERRED = 10   # prefer last 10 years
MIN_YEARS_FALLBACK  = 5    # accept at least 5 years


def safe_float(val: str):
    v = val.strip()
    if v in ("NA", "na", "", "-", "--"):
        return None
    try:
        return float(v.replace(",", "."))
    except ValueError:
        return None


def fetch_station(station):
    """Sækir og þáttir gögn fyrir eina stöð. Skilar lista af árleg-gagna-dicts."""
    try:
        req = urllib.request.Request(
            station["url"],
            headers={"User-Agent": "Mozilla/5.0 (climate-data-fetcher/1.0)"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("iso-8859-1")
    except Exception as e:
        print(f"  ! Mistókst að sækja {station['name']}: {e}")
        return []

    rows = []
    for line in raw.splitlines():
        parts = line.split()
        # Data rows: first token is station ID (integer), second is year (4 digits)
        if len(parts) < 17:
            continue
        try:
            int(parts[0])  # station id
            year = int(parts[1])
            if year < 1900 or year > 2100:
                continue
        except ValueError:
            continue

        rows.append({
            "ar":  year,
            "t":   safe_float(parts[COL_T]),
            "tx":  safe_float(parts[COL_TX]),
            "tn":  safe_float(parts[COL_TN]),
            "r":   safe_float(parts[COL_R]),
            "f":   safe_float(parts[COL_F]),
        })

    return rows


def compute_averages(rows, preferred_n=MIN_YEARS_PREFERRED):
    if not rows:
        return None

    # Sort by year descending, take up to preferred_n most recent
    rows_sorted = sorted(rows, key=lambda r: r["ar"], reverse=True)
    recent = rows_sorted[:preferred_n]

    if len(recent) < MIN_YEARS_FALLBACK:
        return None

    def avg(key):
        vals = [r[key] for r in recent if r[key] is not None]
        return round(mean(vals), 2) if vals else None

    return {
        "ar_fra":  min(r["ar"] for r in recent),
        "ar_til":  max(r["ar"] for r in recent),
        "n_ar":    len(recent),
        "t":       avg("t"),
        "tx":      avg("tx"),
        "tn":      avg("tn"),
        "r":       avg("r"),
        "f":       avg("f"),
    }


def main():
    results = []
    total = len(STATIONS)

    for i, s in enumerate(STATIONS, 1):
        print(f"[{i:3}/{total}] {s['name']} (ID {s['id']})...", end=" ", flush=True)
        rows = fetch_station(s)
        avgs = compute_averages(rows)
        if avgs:
            print(f"OK  t={avgs['t']}°C  r={avgs['r']}mm  f={avgs['f']}m/s  ({avgs['ar_fra']}–{avgs['ar_til']}, {avgs['n_ar']} ár)")
            results.append({
                "id":   s["id"],
                "nafn": s["name"],
                **avgs,
            })
        else:
            print(f"ENGIN GÖGN (fékk {len(rows)} línur)")
        # Small polite delay
        time.sleep(0.05)

    output_path = "static/climate_averages.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "updated":  __import__("datetime").date.today().isoformat(),
            "stations": results,
        }, f, ensure_ascii=False, indent=2)

    print(f"\nDone! {len(results)}/{total} stöðvar vistaðar í {output_path}")


if __name__ == "__main__":
    main()
