#!/bin/env python

import requests
from datetime import datetime, date, timedelta

SHOW_LAST_X_DAYS_OF_NEWS = 7
SHOW_LAST_X_DAYS_OF_INIS = 7
BASE_URL = "https://marktplatz.bewegung.jetzt"
NEWS_URL = BASE_URL + "/search.json?expanded=true&q=%23ankuendigungen-news%20after%3A{}%20order%3Alatest_topic"

VOTING_BASE_URL = "http://localhost:8000" # feature doesn't exist yet on live
VOTING_URL = VOTING_BASE_URL + "/?f=d&f=v&f=a&f=r"

DAYS_OF_WEEK = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "HEUTE"]


def generate_header():
    print("""# DiB Digest
Das Wichtigste aus DEMOKRATIE IN BEWEGUNG in einer wöchentlichen Zusammenfassung
_Ausgabe {} vom {}_

""".format(datetime.today().strftime("%Y.%W"), datetime.today().strftime("%d.%m.%Y")))

def generate_news():
    earliest = datetime.today() - timedelta(days=SHOW_LAST_X_DAYS_OF_NEWS)
    resp = requests.get(NEWS_URL.format(earliest.strftime("%Y-%m-%d")))
    topics = filter(lambda x: x["created_at"] >= earliest.isoformat(),
                    resp.json()["topics"])

    print("## Neuigkeiten & Bekanntmachungen")
    print("")
    if topics:
        for t in topics:
            print(" - {state}[{fancy_title}]({BASE_URL}/t/{id}/{slug}) ({posts_count})".format(
                  BASE_URL=BASE_URL, state="🔒" if t["closed"] else "", **t))

    else:
        print("_Keine Neuigkeiten_")

    print("")


def generate_inis():
    resp = requests.get(VOTING_BASE_URL, headers={
        "X-Requested-With": "XMLHttpRequest",
        "accept": "application/json"})
    inis = resp.json()["content"]["initiatives"]

    vote_urgent = []
    to_vote = []
    discuss_urgent = []
    to_discuss = []
    ended_recently = []

    urgent = date.today() + timedelta(days=SHOW_LAST_X_DAYS_OF_INIS)
    recent = (date.today() - timedelta(days=SHOW_LAST_X_DAYS_OF_INIS)).isoformat()

    for ini in inis:
        if not ini['end_of_this_phase']: continue
        ini['end_of_this_phase'] = date(*map(int, ini['end_of_this_phase'].split("-")))
        if ini['state'] == 'v': # in voting
            if ini['end_of_this_phase'] < urgent:
                vote_urgent.append(ini)
            else:
                to_vote.append(ini)
        elif ini['state'] == 'd': # in discussion
            if ini['end_of_this_phase'] < urgent:
                discuss_urgent.append(ini)
            else:
                to_discuss.append(ini)
        else: # must have closed, check how recently
            if ini['was_closed_at'] and ini['was_closed_at'] > recent:
                ended_recently.append(ini)


    print("## Initiativen")
    print("")
    print("### Zur Abstimmung")

    if vote_urgent or to_vote:
        print("Aktuell stehen die folgenden Initiativen zur Abstimmung:")
        print("")
        for ini in vote_urgent:
            print(" - **[{title}]({BASE_URL}/initiative/{id}-{slug})**, _endet {weekday}_ ".format(
                  BASE_URL=VOTING_BASE_URL,
                  weekday=DAYS_OF_WEEK[ini['end_of_this_phase'].weekday()],
                  **ini))

        for ini in to_vote:
            print(" - [{title}]({BASE_URL}/initiative/{id}-{slug})".format(
                  BASE_URL=VOTING_BASE_URL, **ini))

    else:
        # We show this every time to ensure People know it isn't left out
        print("_Es aktuell keine Initiativen zur Abstimmung_")


    if discuss_urgent or to_discuss:
        print("")
        print("### in Diskussion")
        for ini in discuss_urgent:
            print(" - **[{title}]({BASE_URL}/initiative/{id}-{slug})**, _endet {weekday}_ ".format(
                  BASE_URL=VOTING_BASE_URL,
                  weekday=DAYS_OF_WEEK[ini['end_of_this_phase'].weekday()],
                  **ini))

        for ini in to_discuss:
            print(" - [{title}]({BASE_URL}/initiative/{id}-{slug})".format(
                  BASE_URL=VOTING_BASE_URL,**ini))

        print("")

    if ended_recently:
        print("### kürzlich abgestimmt")
        print("")
        for ini in ended_recently:
            print(" - {icon} [{title}]({BASE_URL}/initiative/{id}-{slug})".format(
                  BASE_URL=VOTING_BASE_URL,
                  icon="👍" if ini['state'] == 'a' else "👎",
                  **ini))

        print("")

def generate_events():
    print("## Veranstaltungen")
    print("_noch zu erstellen_")
    print("")

def generate_community():
    print("## Community Highlights")
    print("_noch zu erstellen_")
    print("")

    print("## Zitat der Woche")
    print("_noch zu erstellen_")
    print("")

def main():
    generate_header()
    generate_news()
    generate_inis()
    generate_events()
    generate_community()

if __name__ == '__main__':
    main()