import sys
import time

import requests
from bs4 import BeautifulSoup
from typing import List


class Preis:
    _haendler: str
    _preis: float

    def __init__(self, haendler: str, preis: float):
        self._haendler = haendler
        self._preis = preis

    def __str__(self):
        return f"Preis[haendler={self._haendler}, preis={self._preis}]"

    def haendler(self):
        return self._haendler

    def preis(self):
        return self._preis

    def __repr__(self):
        return self.__str__()


class Muenze:
    _name: str
    _katid: int
    _jahrgang: int
    _preise: List[Preis]

    def __init__(self, name: str, jahrgang: int, katid: int):
        self._name = name
        self._jahrgang = jahrgang
        self._katid = katid
        self._preise = []

    def add_preis(self, preis: Preis):
        self._preise.append(preis)

    def katid(self):
        return self._katid

    def preise(self):
        return self._preise

    def jahrgang(self):
        return self._jahrgang

    def name(self):
        return self._name

    def __str__(self):
        return f"Muenze[name={self._name}, jahrgang={self._jahrgang}, katid={self._katid}, preise={self._preise}]"


if __name__ == '__main__':

    alle_muenzen = []
    file = open(sys.argv[1], 'r')
    for zeile in file.readlines():
        splitted = zeile.split(";")
        if splitted[0] == "name":
            continue
        muenze = Muenze(splitted[0], int(splitted[1]), int(str.strip(splitted[2])))
        alle_muenzen.append(muenze)

    unixdate = time.time()

    alle_haendler = []

    for muenze in alle_muenzen:

        response = requests.get(f'https://www.gold.de/ajax/preisvergleich.php?'
                                f'katid={muenze.katid()}'
                                f'&get_jahrgang={muenze.jahrgang()}'
                                f'&get_mode=kaufen&get_invest=&get_stueckelung=1 oz'
                                f'&get_orderby=&get_filter_anzahl=&get_groupby=0'
                                f'&seite=&_={unixdate}')
        soup = BeautifulSoup(response.content, 'html.parser')
        all_rows = soup.find_all('tr')
        for row in all_rows:
            all_tds = row.find_all('td')
            if all_tds:
                alle_preise = []
                last_td = all_tds[len(all_tds) - 1]
                price_div = last_td.find_all('div')[0]
                text = price_div.text
                if 'EUR' in text and 'Günstigere Paketpreise' not in text:
                    third_td = all_tds[2]
                    link = third_td.find('a')
                    preis = Preis(str.strip(link.text), float(str.replace(str.split(text, sep=" ")[0], ",", ".")))
                    muenze.add_preis(preis)
                    if not preis.haendler() in alle_haendler:
                        alle_haendler.append(preis.haendler())

    alle_zeilen = []
    zeile = "Name;Jahrgang;"
    alle_haendler.sort()

    for haendler in alle_haendler:
        zeile += haendler + ";"
    zeile += "\n"
    alle_zeilen.append(str(zeile))

    for muenze in alle_muenzen:
        zeile = f"{muenze.name()};{muenze.jahrgang()};"
        muenze.preise().sort(key=lambda x: x.haendler())

        for haendler in alle_haendler:
            exists = False
            preis_einfuegen: str
            for preis in muenze.preise():
                if preis.haendler() == haendler:
                    exists = True
                    preis_einfuegen = str.replace(str(preis.preis()), ".", ",")
                    break
            if exists:
                zeile += f"{preis_einfuegen}"
            zeile += ";"

        zeile += "\n"
        alle_zeilen.append(zeile)

    file_out = open(sys.argv[2], "w")
    file_out.writelines(alle_zeilen)
