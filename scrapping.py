from bs4 import BeautifulSoup
from requests import get
from utility import format_name, format_wr, format_matches, get_champions
from os import path
import pandas as pd


def assembly_url(champion, opponent):
    return f"https://u.gg/lol/champions/{format_name(champion)}/build/top?opp={format_name(opponent)}"


def fill_champion(champion):
    matchups = {}
    champions = get_champions()
    for op in champions:
        op = op.replace("\n", "")
        if op == champion:
            continue
        print(f"Scrapping {champion} x {op}")
        url = assembly_url(champion, op)
        page = get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        divs = soup.find_all("div", {"class": "value"})
        wr = divs[0].text
        matchups[op] = wr

    with open(f"matchups/{champion}", "w") as f:
        f.write("opponent,wr\n")
        for op in matchups.keys():
            f.write(f"{op},{format_wr(matchups[op])}\n")


def fill_all():
    champions = get_champions()
    for c in champions:
        c = c.replace("\n", "")
        if path.exists(f"matchups/{c}"):
            continue
        fill_champion(c)


def fill_champions():
    df = pd.read_csv("toplaners")
    matches = []
    wrs = []
    for c in df["champion"]:
        url = f"https://u.gg/lol/champions/{format_name(c)}/build/top"
        page = get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        divs = soup.find_all("div", {"class": "value"})
        match = divs[5].text
        wr = divs[1].text
        wrs.append(format_wr(wr))
        matches.append(format_matches(match))

    df["matches"] = matches
    df["wr"] = wrs
    del df['Unnamed: 0']
    del df['Unnamed: 0.1']
    df.to_csv("toplaners", index=False)


fill_champions()