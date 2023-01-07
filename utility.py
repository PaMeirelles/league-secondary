import pandas as pd

def filter_champions():
    with open("toplaners", "r") as f:
        lines = f.readlines()
        lines = [x for i, x in enumerate(lines) if (i - 2) % 8 == 0]

    with open("toplaners", "w") as f:
        for line in lines:
            f.write(line)


def format_name(name):
    forbidden = [' ', '.', "'"]
    for f in forbidden:
        name = name.replace(f, "")
    return name.lower()


def format_wr(wr):
    return float(wr.replace("%", "")) / 100


def format_matches(matches):
    return int(matches.replace(",", ""))


def get_champions():
    df = pd.read_csv("toplaners")
    return [x.replace("\n", "") for x in df["champion"]]
