"""
Pulls Baseball data from rotoguru and saves it as csv
"""
import pandas as pd
from bs4 import BeautifulSoup
import requests
import os
import argparse


def get_rg_baseb_data(day, month, year, site="fd") -> str():
    """
    Writes response to path if one is given, else only return
    """
    BASE_URL = "http://rotoguru1.com/cgi-bin/byday.pl"

    site_map = {"FanDuel": "fd", "DraftKings": "dk", "YahooDFS": "yh"}

    r = requests.get(
        BASE_URL,
        params={
            "game": site_map[site],
            "month": month,
            "day": day,
            "year": year,
        },
    )
    print("Downloaded day={} month={} year={}".format(day, month, year))
    if r.text == "Invalid date":
        raise ValueError("Invalid date provided")

    return r.text


def parse_rg_html(html: str) -> pd.DataFrame():

    soup = BeautifulSoup(html, features="lxml")

    table = soup.find("table", {"cellspacing": 5})
    table_rows = table.find_all("tr")

    res = []
    for tr in table_rows:
        td = tr.find_all("td")
        row = [tr.text.strip() for tr in td]
        if row not in ["Jump to:     Pitchers   |   Hitters   |"]:
            res.append(row)

    df = pd.DataFrame(res)
    df = df.rename(
        columns={
            0: "Position",
            1: "Player",
            2: "Points",
            3: "Salary",
            4: "Team",
            5: "Opp",
            6: "Score",
            7: "StatSummary",
        }
    )
    df = df[df["Position"] != "Jump to:     Pitchers   |   Hitters   |"]
    df = df[df["Position"] != "Hitters"]
    df = df.iloc[2:-1].reset_index().drop("index", axis=1)
    return df


def __main(args):
    data = get_rg_baseb_data(args.day, args.month, args.year, args.site)
    df = parse_rg_html(data)
    if os.path.exists(args.path):
        df.to_csv(
            os.path.join(
                args.path,
                "{}_{}_{}_{}.csv".format(
                    args.day, args.month, args.year, args.site
                ),
            )
        )


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Download baseball data from rotoguru"
    )
    parser.add_argument("day", type=int, help="Day of month")
    parser.add_argument("month", type=int, help="Month of year")
    parser.add_argument("year", type=int, help="MLB Season")
    parser.add_argument(
        "--site",
        metavar="site",
        help="Site to pull for",
        choices=["DraftKings", "FanDuel", "YahooDFS"],
        default="FanDuel",
    )
    parser.add_argument(
        "--path",
        metavar="path",
        help="Where to save data to",
        type=str,
        default=".",
    )
    args = parser.parse_args()
    __main(args)
