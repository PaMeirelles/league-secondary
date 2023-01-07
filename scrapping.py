from bs4 import BeautifulSoup
from requests import get
from utility import format_name, format_wr, format_matches, get_champions
from os import path
import pandas as pd
import time


def assembly_url(champion, opponent, elo):
    return f"https://u.gg/lol/champions/{format_name(champion)}/build/top?opp={format_name(opponent)}&rank={elo}"


def fill_champion(champion, elo):
    matchups = {}
    champions = get_champions()
    for op in champions:
        op = op.replace("\n", "")
        if op == champion:
            continue
        print(f"Scrapping {champion} x {op}")
        url = assembly_url(champion, op, elo)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        page = get(url, headers=headers)
        if page.status_code != 200:
            print(page.status_code, url)
            time.sleep(60)
            fill_champions(elo)
            return
        soup = BeautifulSoup(page.content, "html.parser")
        divs = soup.find_all("div", {"class": "value"})
        wr = divs[0].text
        matchups[op] = wr
    with open(f"{elo}/matchups/{champion}", "w") as f:
        f.write("opponent,wr\n")
        for op in matchups.keys():
            f.write(f"{op},{format_wr(matchups[op])}\n")


def fill_all(elo):
    champions = get_champions()
    for c in champions:
        c = c.replace("\n", "")
        if path.exists(f"{elo}/matchups/{c}"):
            continue
        fill_champion(c, elo)


def fill_champions(elo):
    df = pd.read_csv(f"{elo}/toplaners")
    matches = []
    wrs = []
    for c in df["champion"]:
        url = f"https://u.gg/lol/champions/{format_name(c)}/build/top?rank={elo}"
        page = get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        divs = soup.find_all("div", {"class": "value"})
        match = divs[5].text
        wr = divs[1].text
        wrs.append(format_wr(wr))
        matches.append(format_matches(match))

    df["matches"] = matches
    df["wr"] = wrs
    df.to_csv(f"{elo}/toplaners", index=False)


fill_all("silver")