#!/bin/env python

import requests
from datetime import datetime, timedelta

SHOW_LAST_X_DAYS_OF_NEWS = 7
BASE_URL = "https://marktplatz.bewegung.jetzt"
NEWS_URL = BASE_URL + "/search.json?expanded=true&q=%23ankuendigungen-news%20after%3A{}%20order%3Alatest_topic"

def generate_header():
    print("""# DiB Digest
Das Wichtigste aus DEMOKRATIE IN BEWEGUNG in einer wöchentlichen Zusammenfassung

""")

def generate_news():
    earliest = datetime.today() - timedelta(days=SHOW_LAST_X_DAYS_OF_NEWS)
    resp = requests.get(NEWS_URL.format(earliest.strftime("%Y-%m-%d")))
    topics = filter(lambda x: x["created_at"] >= earliest.isoformat(),
                    resp.json()["topics"])

    print("## Neuigkeiten & Bekanntmachungen")
    print("")
    if topics:
        for t in topics:
            print(" - [{fancy_title}]({BASE_URL}/t/{id}/{slug})".format(BASE_URL=BASE_URL, **t))

    else:
        print("_Keine Neuigkeiten_")

    print("")

def generate_inis():
    print("## Initiativen")
    print("")
    print("### in Abstimmung")
    print("")
    print("_noch zu erstellen_")
    print("### in Diskussion")
    print("")
    print("_noch zu erstellen_")
    print("")
    print("### Neu abgestimmt")
    print("")
    print("_noch zu erstellen_")
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