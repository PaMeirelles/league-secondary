import pandas as pd
from utility import get_champions
from os import path


def pair(c1, c2):
    df1 = pd.read_csv(f"matchups/{c1}")
    df2 = pd.read_csv(f"matchups/{c2}")

    df3 = df1.merge(df2, left_on="opponent", right_on="opponent")
    df3["wr_pair"] = df3[["wr_x", "wr_y"]].agg("max", 1)
    m = [df3["wr_pair"] == df3["wr_x"]]
    for i in range(len(m[0])):
        if m[0][i]:
            m[0][i] = c1
        else:
            m[0][i] = c2
    df3["pick"] = m[0]

    a, b = df1[df1["opponent"] == c2]["wr"], df2[df2["opponent"] == c1]["wr"]
    df3 = pd.concat([df3, pd.DataFrame({"opponent": c1, "wr_pair": b, "pick": c2})])
    df3 = pd.concat([df3, pd.DataFrame({"opponent": c2, "wr_pair": a, "pick": c1})])
    return df3


def get_ban(df, duo, champion, show=False):
    d = df["wr_pair"]
    w = df["matches"]

    final_wr = (d * w).sum() / w.sum()
    df["Ban score"] = ((final_wr - d) * w)

    df.loc[df["opponent"] == champion, "Ban score"] = -float("inf")
    df.loc[df["opponent"] == duo, "Ban score"] = -float("inf")

    id_ban = df["Ban score"].idxmax()
    if show:
        print(f"Ban {df['opponent'][id_ban]}")
    return df['opponent'][id_ban]


def pair_wr(c1, c2, show=False):
    df = pair(c1, c2)
    df2 = pd.read_csv("toplaners")

    df3 = df.merge(df2, left_on="opponent", right_on="champion")

    banned = get_ban(df3, c2, c1, show)

    df3 = df3[df3["opponent"] != banned]

    d = df3["wr_pair"]
    w = df3["matches"]

    final_wr = (d * w).sum() / w.sum()
    if show:
        print(df3[["opponent", "pick"]])
    return final_wr


def perfect_match(champion):
    champions = get_champions()
    pairs = {p: pair_wr(champion, p) for p in champions if path.exists(f"matchups/{p}")}
    return sorted(pairs.items(), key=lambda x: x[1], reverse=True)


print(perfect_match("Camille"))
print(pair_wr("Camille", "Dr. Mundo", True))

