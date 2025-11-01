"""
Bear Tracking Analysis
----------------------
This script processes and analyzes brown bear GPS data.
Written as part of the Programming 1 course at University of Ljubljana.
Original dataset and test files are not included.

All code implementation below is my own.
Course materials and test data © Professor Janez Demšar, Faculty of Information and Computer Science, University of Ljubljana.
"""

import csv
import numpy as np
from datetime import datetime


def preberi_podatke():
    vsota = 0
    f = open("Brown bear Slovenia 1993-1999.csv")
    reader = csv.DictReader(f)
    for vrstica in reader:
        vsota += 1

    imena = np.empty(vsota, dtype="U50")
    datumi = np.empty((vsota, 3), dtype=object)
    dnevi = np.empty(vsota, dtype=int)
    xy = np.empty((vsota, 2), dtype=float)

    f = open("Brown bear Slovenia 1993-1999.csv")
    min_datum = None
    for i, vrstica in enumerate(csv.DictReader(f)):

        imena[i] = vrstica['individual-local-identifier']

        datum = datetime.strptime(vrstica['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
        datumi[i] = datum.year, datum.month, datum.day

        if min_datum is None or datum < min_datum:
            min_datum = datum

        xy[i] = (
            (float(vrstica['location-lat']) - 45.9709794) * (40007 / 360),
            (float(vrstica['location-long']) - 14.1118016) * (40075 * np.cos(np.radians(45.9709794)) / 360)
        )

    for i in range(vsota):
        datum = datetime(datumi[i][0], datumi[i][1], datumi[i][2])
        dnevi[i] = (datum.date() - min_datum.date()).days

    return  imena, datumi, dnevi, xy


imena, datumi, dnevi, xy = preberi_podatke()



def medvedi():
    return sorted(list(set(imena)))



def n_meritev():
    meritve = {}
    for ime in imena:
        if ime in meritve:
            meritve[ime] += 1
        else:
            meritve[ime] = 1

    return meritve


def razponi():

    razpon = {}
    for i, ime in enumerate(imena):
        razpon[imena[i]] = dnevi[i]

    for medved, zadnji_dan in razpon.items():
        prvi_dan = min(dnevi[i] for i, ime in enumerate(imena) if ime == medved)
        razpon[medved] = zadnji_dan - prvi_dan

    return razpon


def n_zaporednih_meritev(medved):
    stevilo = 0
    for i, dan in enumerate(dnevi[1:]):
        if imena[i] == medved and dnevi[i]== (dnevi[i - 1] + 1):
            stevilo += 1
    return stevilo

#z numpyjem
def n_zaporednih_meritev(medved):
   medvedi_mask = (imena == medved)
   dnevi_razlike = np.diff(dnevi)
   zaporedne_mask = (dnevi_razlike == 1)
   zaporedne = medvedi_mask[1:] & medvedi_mask[:-1] & zaporedne_mask
   stevilo = np.sum(zaporedne)

   return stevilo

def zaporedne_meritve():
     zap_meritve = {}
     stevilo_m = 0
     for i, ime in enumerate(imena):
         if imena[i - 1] == imena[i] and dnevi[i] == dnevi[i - 1] + 1:
             stevilo_m += 1
         elif imena[i - 1] != imena[i]:
             stevilo_m = 0
         zap_meritve[ime] = stevilo_m
     return zap_meritve

def dnevna_razdalja(medved):
    medvedi_mask = (imena == medved)
    dnevi_razlike = np.diff(dnevi)
    zaporedne_mask = (dnevi_razlike == 1)
    zaporedne = medvedi_mask[1:] & medvedi_mask[:-1] & zaporedne_mask
    prvi = xy[:-1][zaporedne]
    drugi = xy[1:][zaporedne]
    dnevna_razdalja = np.sqrt(np.sum((prvi - drugi)**2, axis = 1))
    povprecna = np.mean(dnevna_razdalja)

    return povprecna

def dnevne_razdalje():
    razdalje = {}
    for medved in np.unique(imena):
        medvedi_mask = (imena == medved)
        dnevi_razlike = np.diff(dnevi)
        zaporedne_mask = (dnevi_razlike == 1)
        zaporedne = medvedi_mask[1:] & medvedi_mask[:-1] & zaporedne_mask
        prvi = xy[:-1][zaporedne]
        drugi = xy[1:][zaporedne]
        dnevna_razdalja = np.sqrt(np.sum((prvi - drugi) ** 2, axis=1))
        povprecna = np.mean(dnevna_razdalja)

        razdalje[medved] = povprecna

    return razdalje

def dnevne_razdalje():
    razdalje = {}
    for medved in np.unique(imena):
        razdalje[medved] = dnevna_razdalja(medved)

    return razdalje

def popotnik():
    razdalje_z_nan = dnevne_razdalje()
    razdalje ={ime: r for ime, r in razdalje_z_nan.items() if not np.isnan(r)}
    max_r = max(razdalje.values())
    max_ime = [ime for ime, r in razdalje.items() if r == max_r]

    if max_ime:
        return max_ime[0]

def izlet():
    dnevna_razdalja_max = 0
    xy_i = 0
    max_r = 0

    for medved in np.unique(imena):
        medvedi_mask = (imena == medved)
        dnevi_razlike = np.diff(dnevi)
        zaporedne_mask = (dnevi_razlike == 1)
        zaporedne = medvedi_mask[1:] & medvedi_mask[:-1] & zaporedne_mask
        prvi = xy[:-1][zaporedne]
        drugi = xy[1:][zaporedne]
        dnevna_razdalja = np.sqrt(np.sum((prvi - drugi) ** 2, axis=1))
        if len(dnevna_razdalja) > 0 and np.max(dnevna_razdalja) > dnevna_razdalja_max:
            i = np.argmax(dnevna_razdalja)

            max_r = np.max(dnevna_razdalja)
            xy_i = np.where(np.all(drugi[i] == xy, axis=1))[0][0]

            dnevna_razdalja_max = np.max(dnevna_razdalja)

    return imena[xy_i], datumi[xy_i], max_r




def mesecna_razdalja():  # povprecna razdalja vseh skupaj za vsak mesec
    meseci_razdalje = {mesec: [] for mesec in range(1, 13)}

    for mesec in range(1, 13):
        mesec_mask = (mesec == datumi[:, 1])

        medvedi_mask = (imena[1:] == imena[:-1])
        dnevi_razlike = np.diff(dnevi)
        zaporedne_mask = (dnevi_razlike == 1)
        zaporedne = medvedi_mask & zaporedne_mask & mesec_mask[:-1]

        prvi = xy[:-1][zaporedne]
        drugi = xy[1:][zaporedne]
        dnevna_razdalja = np.sqrt(np.sum((prvi - drugi) ** 2, axis=1))

        meseci_razdalje[mesec].extend(dnevna_razdalja)

    povprecne = []
    for meseci, razdalje in meseci_razdalje.items():
        povprecne.append(np.mean(razdalje))

    return povprecne

def leni_meseci(s):
    s2 = s + s
    vsote = [sum(s2[i:i + 3]) for i in range(len(s))][:13]
    indeks = vsote.index(min(vsote))
    return (indeks + 1)

def lenoba(s):
    s2 = s + s
    i = leni_meseci(s) - 1
    leni = sum(s2[i:i + 3]) / 3
    povprecna_letna = sum(s) / 12
    razmerje = leni / povprecna_letna

    return razmerje


def povprecna_razdalja(medved1, medved2):
    medvedi_mask1 = (imena == medved1)
    medvedi_mask2 = (imena == medved2)

    prvi = xy[medvedi_mask1]
    drugi = xy[medvedi_mask2]

    razdalje = []

    for xy1 in prvi:
        for xy2 in drugi:
            razdalja = np.sqrt(np.sum((xy1 - xy2) ** 2))
            razdalje.append(razdalja)

    return np.mean(razdalje)

def povprecne_razdalje():
    razdalje_po_parih = {}
    medvedi_po_abecedi = sorted(np.unique(imena))
    for i, medved1 in enumerate(medvedi_po_abecedi):
        for j, medved2 in enumerate(medvedi_po_abecedi[1:]):
            if medved1 != medved2:
                par = tuple(sorted([medved1, medved2]))
                razdalja = povprecna_razdalja(medved1, medved2)
            razdalje_po_parih[par] = razdalja

    return razdalje_po_parih


def prijatelji():
    razdalje_pari = povprecne_razdalje()
    for par, razdalja in razdalje_pari.items():
        pari_tabela = []

        for par, razdalja in razdalje_pari.items():
            pari_tabela.append((par[0], par[1], razdalja))

        pari_tabela.sort(key=lambda x: x[2])  # sortira po razdaljah
        prvih_10 = pari_tabela[:10]

    for ime1, ime2, razdalja in prvih_10:
        print(f'{ime1:>20} : {razdalja:5.2f} : {ime2}')

def bffl():
    razdalje_pari = povprecne_razdalje()
    for par, razdalja in razdalje_pari.items():
        pari_tabela = []

        for par, razdalja in razdalje_pari.items():
            pari_tabela.append((par[0], par[1], razdalja))

        pari_tabela.sort(key=lambda x: x[2])
        prvi = pari_tabela[0]

    return prvi[:2]



def druzabnost(medved, kraji, k):
    medved_mask = (imena == medved)
    koordinate = xy[medved_mask]

    novikraji = np.empty((len(kraji), 2), dtype=float)
    for i, kraj in enumerate(kraji):
        novikraji[i] = (
            (float(kraj[0]) - 45.9709794) * (40007 / 360),
            (float(kraj[1]) - 14.1118016) * (40075 * np.cos(np.radians(45.9709794)) / 360)
        )

    blizu = np.zeros(len(koordinate), dtype=bool) # array s samimi false

    for kraj in novikraji:
        razdalje = np.sqrt(np.sum((koordinate - kraj)**2, axis=1))
        blizu |= (razdalje <= k)

    return np.sum(blizu)



def tezisce_delovanja(medved, kraji):

    medved_mask = (imena == medved)
    koordinate = xy[medved_mask]

    novikraji = np.empty((len(kraji), 2), dtype=float)
    for i, kraj in enumerate(kraji):
        novikraji[i] = (
            (float(kraj[0]) - 45.9709794) * (40007 / 360),
            (float(kraj[1]) - 14.1118016) * (40075 * np.cos(np.radians(45.9709794)) / 360)
        )
        najkraji = []
        najkraji_counts = [0] * len(kraji)

        for koordinata in koordinate:
            najrazdalja = float('inf')
            najkraj_index = None

            for i, kraj in enumerate(novikraji):
                razdalja = np.sqrt(np.sum((np.reshape(kraj, (1, 2)) - np.reshape(koordinata, (1, 2))) ** 2, axis=1))

                if razdalja < najrazdalja:
                    najrazdalja = razdalja
                    najkraj_index = i

            najkraji.append(tuple(novikraji[najkraj_index]))
            najkraji_counts[najkraj_index] += 1


    return (np.array(najkraji_counts)/sum(najkraji_counts))


def obiskovalci(kraji):

    mnozice = [set() for _ in range(len(kraji))]
    for medved in np.unique(imena):
        blizine = tezisce_delovanja(medved, kraji)
        i = np.argmax(blizine)
        mnozice[i].add(medved)
    return mnozice






















