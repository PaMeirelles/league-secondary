import pandas as pd
from utility import get_champions
from os import path
from itertools import combinations


def pair(champions, elo, relative=False, bonus=None):
    if bonus is None:
        bonus = []
    tops = pd.read_csv(f"{elo}/toplaners")
    dfs = [pd.read_csv(f"{elo}/matchups/{c}").rename(columns={"wr": f"wr{i}"}) for i, c in enumerate(champions)]
    df = dfs[0]

    for i, d in enumerate(dfs[1:]):
        df = df.merge(d, left_on="opponent", right_on="opponent", how="outer")

    for i, b in enumerate(bonus):
        df[f"wr{i}"] += b

    if relative:
        normal = [tops[tops["champion"] == c]["wr"].values[0] for c in champions]
    else:
        normal = [0 for _ in range(len(champions))]

    for i in range(len(champions)):
        df[f"wr{i}"] -= normal[i]

    df["bonus"] = df[[f"wr{i}" for i in range(len(champions))]].agg("max", 1)
    picks = []
    for i, row in df.iterrows():
        for j in range(len(champions)):
            if row[f"wr{j}"] == row["bonus"]:
                picks.append(champions[j])
                break

    df["pick"] = picks
    return df


def get_ban(df, champions, show=False):
    d = df["bonus"]
    w = df["matches"]

    final_wr = (d * w).sum() / w.sum()
    df["Ban score"] = ((final_wr - d) * w)

    for c in champions:
        df.loc[df["opponent"] == c, "Ban score"] = -float("inf")

    id_ban = df["Ban score"].idxmax()
    if show:
        print(f"Ban {df['opponent'][id_ban]}")
    return df['opponent'][id_ban]


def pair_wr(champions, elo, show=False, relative=False, bonus=None):
    if bonus is None:
        bonus = []
    df = pair(champions, elo, relative, bonus=bonus)
    df2 = pd.read_csv(f"{elo}/toplaners")

    df3 = df.merge(df2, left_on="opponent", right_on="champion")

    banned = get_ban(df3, champions, show)

    df3 = df3[df3["opponent"] != banned]

    d = df3["bonus"]
    w = df3["matches"]
    final_wr = (d * w).sum() / w.sum()
    if show:
        print(df3[["opponent", "pick", "bonus"]])
    # df3[["opponent", "pick"]].to_excel(f"excel/{c1}/{c2}.xlsx")
    return final_wr


def perfect_match(champion, team_size, elo, relative=False, bonus=None):
    if bonus is None:
        bonus = []
    champions = get_champions()
    teams = [[champion] + list(x) for x in combinations([c for c in champions
                                                         if path.exists(f"{elo}/matchups/{c}")],
                                                        team_size - 1)]
    wrs = [(p, pair_wr(p, elo, relative=relative, bonus=bonus)) for p in teams]
    return sorted(wrs, key=lambda x: x[1], reverse=True)


perfect_match("Camille", 3, "silver")
