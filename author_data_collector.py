'''
Author Data Collector
---------------------
This program downloads and processes author data from provided HTML files.

Developed as part of Programming 1 course at University of Ljubljana.
The URLs and test suite included in the original assignment were provided by the instructor
and are not included here.

All code implementation below is my own.
Course materials and test data © Professor Janez Demšar, Faculty of Information and Computer Science, University of Ljubljana.
'''


import os
import string
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import json



def prenesi_podatke():
    # preverit direktorij
    if not os.path.exists("authors"):
        os.mkdir("authors")

    for crka in string.ascii_lowercase:
        dat_pot = os.path.join("authors", f"{crka}.html")
        # če še ni datoteke v direktoriju
        if not os.path.exists(dat_pot):
            url = f"https://ucilnica.fri.uni-lj.si/pluginfile.php/217381/mod_folder/content/0/{crka}.html"
            vsebina = urlopen(url).read()

            with open(dat_pot, "wb") as file:
                file.write(vsebina)
            # file = open(dat_pot)
            # file.write(vsebina)
            # file.close()


def avtorji(priimek):
    for crka in priimek[0]:
        file = open(f"authors/{crka}.html", encoding="utf-8")
        vsebina = file.read()
    soup = BeautifulSoup(vsebina, 'html.parser')

    authors = []
    for link in soup.find_all("h2"):
        celo_ime = link.text
        surname = link.text.split(",")[0]

        if surname == priimek:
            authors.append(celo_ime)

    return authors


def razberi_avtorja(s):
    vzorec = re.compile(r",\s(\d+)?(\??)?( BC\s*)?-(\d+)?(\??)?( BC\s*)?")
    mo = vzorec.search(s)

    #da se ne ustavi ko najde prvi -
    while mo and mo.group() == '-':
        mo = vzorec.search(s, mo.end())
        if mo is not None and mo.group() == '-':
            continue
        break

    if mo == None:
        return None
    else:
        rojstvo, vpr1, bc_r, smrt, vpr2, bc_s = mo.groups()

    celo_ime = s.split(", ")
    priimek = celo_ime[0]
    imena = celo_ime[1:-1]


    if rojstvo is not None:
        rojstvo = int(rojstvo)
    if smrt is not None:
        smrt = int(smrt)

    if bc_r:
        rojstvo = -int(rojstvo)
    if bc_s:
        smrt = -int(smrt)

    return priimek, imena, rojstvo, smrt


def zberi_podatke(crke):
    if crke == "":
        crke = string.ascii_lowercase
    avtorji = {}
    if not os.path.exists("authors"):
        prenesi_podatke()
    else:
        for crka in crke:
            file = open(f"authors/{crka}.html", encoding="utf-8")
            vsebina = file.read()
            soup = BeautifulSoup(vsebina, 'html.parser')

            for vrstica in soup.find_all("h2"):
                celo_ime = vrstica.text


                avtor_podatki = razberi_avtorja(celo_ime)

                if avtor_podatki is not None:

                    priimek, ime, rojen, umrl = avtor_podatki

                    if priimek not in avtorji:
                        avtorji[priimek] = [avtor_podatki]
                    else:
                        avtorji[priimek].append(avtor_podatki)

    return avtorji

if "authors.json" not in os.listdir():
    if not os.path.exists("authors"):
        prenesi_podatke()

    podatki = zberi_podatke("")
    f = open("authors.json", "w", encoding="utf-8")
    json.dump(podatki, f)
    f.close()


def v_obdobju(rojen, umrl, zacetek, konec):
    if rojen != None and umrl != None:

        if (rojen <= konec and umrl >= zacetek):
            return True
        else:
            return False
    else:
        if rojen == None:
            if (umrl >= zacetek and umrl <= konec):
                return True
            else:
                return False
        elif umrl == None:
            if rojen <= konec and rojen >= zacetek:
                return True
            else:
                return False


def avtorji_v_obdobju(zacetek, konec):

    avtorji = []
    with open("authors.json", encoding= "utf-8") as f:
        slovar = json.load(f)

    for priimek, podatki in slovar.items():
        for avtor in podatki:
            priimek, ime, rojen, umrl = avtor


            if rojen != None and umrl != None:
                if v_obdobju(rojen, umrl, zacetek, konec) == True:
                    avtorji.append(avtor)

    return sorted(avtorji)


def razpon():

    with open("authors.json", encoding= "utf-8") as f:
        slovar = json.load(f)

    rojstva = []
    smrti = []
    for priimek, podatki in slovar.items():
        for avtor in podatki:
            priimek, ime, rojen, umrl = avtor
            if rojen != None and umrl != None:
                rojstva.append(rojen)
                smrti.append(umrl)

    return min(rojstva), max(smrti)


def pokritost(zacetek, konec):
    st_avtorjev = []
    razlika = konec - zacetek

    for i in range(0, razlika + 1):
        st_avtorjev.append(len(avtorji_v_obdobju(zacetek + i, zacetek + i)))

    return st_avtorjev


def razberi_delo(s):
    vzorec =  r'^([^\n]+.*?) \(([\w\- ]+)\) \(as Author\)$'

    match = re.match(vzorec, s)

    if match != None:
        jezik = match.group(2)
        naslov = match.group(1)

        return naslov, jezik

    return None


def dela():
    dela = []
    for crka in string.ascii_lowercase:
        file = open(f"authors/{crka}.html", encoding="utf-8")
        vsebina = file.read()
        soup = BeautifulSoup(vsebina, 'html.parser')


        for link in soup.find_all("li", {"class": "pgdbetext"} ):

            delo = razberi_delo(link.text)
            if delo != None:
                naslov, jezik = delo
            else:
                continue

            avtor_link = link.parent.find_previous_sibling("h2")

            if avtor_link != None:
                avtor = razberi_avtorja(avtor_link.text)

                if avtor != None:
                    priimek, ime, rojen, umrl = avtor
                    dela.append((naslov, jezik, priimek, ime, rojen, umrl))

    return dela


if "works.json" not in os.listdir():
    if not os.path.exists("authors"):
        prenesi_podatke()

    podatki = dela()
    f = open("works.json", "w", encoding="utf-8")
    json.dump(podatki, f)
    f.close()


def dela_po_jezikih():
    jeziki = {}
    with open("works.json", encoding= "utf-8") as f:
        podatki = json.load(f)

        for en in podatki:
            naslov, jezik, priimek, ime, rojen, umrl = en

            if jezik not in jeziki:
                jeziki[jezik] = 1
            else:
                jeziki[jezik] += 1


    return jeziki


def preveri_delo(delo, avtor=None, naslov=None, jezik=None, leto=None):

    naslov1, jezik1, priimek, ime, rojen, umrl = delo
    celo_ime = " ".join(ime) + " " + priimek
    skupno = True
    if avtor != None and avtor not in celo_ime :
        skupno = False
    if naslov != None and naslov not in naslov1:
        skupno = False
    if jezik != None and jezik != jezik1:
        skupno = False
    if leto != None and v_obdobju(rojen, umrl, leto, leto) != True:
        skupno = False
    if rojen == None or umrl == None:
        skupno = False

    return skupno


def poisci(avtor=None, naslov=None, jezik=None, leto=None):
    dela = []
    with open("works.json", encoding= "utf-8") as f:
        podatki = json.load(f)

        for delo in podatki:
            if preveri_delo(delo, avtor, naslov, jezik, leto) == True:
                dela.append(delo)

    return dela








