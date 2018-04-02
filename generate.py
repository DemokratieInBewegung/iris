#!/bin/env python

import requests
from datetime import datetime, date, timedelta
import dateutil.parser
import os

if not "DC_TOKEN" in os.environ:
    print("Please specify the Discourse API token as DC_TOKEN!")
    exit(1)

DC_TOKEN = os.environ['DC_TOKEN']

SHOW_LAST_X_DAYS_OF_NEWS = 8
SHOW_LAST_X_DAYS_OF_INIS = 7

BASE_URL = "https://marktplatz.bewegung.jetzt"
NEWS_URL = BASE_URL + "/search.json?expanded=true&q=category:13 after:{} order:latest_topic"
EVENTS_URL = BASE_URL + "/search.json?expanded=true&q=%23partei%20tags%3Averanstaltung%20status%3Aopen%20order%3Alatest_topic"
RECRUITING_URL = BASE_URL + "/search.json?api_key={}&api_username=system&expanded=true&q=category:94 status:open after:2017-10-10 order:latest_topic".format(DC_TOKEN)
TOP_URL = BASE_URL + "/top/weekly.json"
QUOTES_URL = "https://marktplatz.bewegung.jetzt/t/lustige-dib-zitate/10175.json?api_key={}&api_username=system".format(DC_TOKEN)

TODAY = datetime.today()
if TODAY.weekday() != 6:
    # If we aren't on Sunday, move to next Sunday
    TODAY += timedelta(days=6 - TODAY.weekday())

VOTING_BASE_URL = "https://abstimmen.bewegung.jetzt" # feature doesn't exist yet on live
VOTING_URL = VOTING_BASE_URL + "/?f=d&f=v&f=a&f=r"

DAYS_OF_WEEK = ["Montag", "Dienstag", "Mittwoch", "Donnerstag",
                "Freitag", "Samstag", "Sonntag"]


def generate_header():
    yield ("""
extends: default.liquid
title: HIER_EINTRAGEN
edition: {edition}
date: {date} 4:00:00 +0100
email_subject: HIER_EINTRAGEN — Iris {edition}

---

""".format(edition=TODAY.strftime("%Y/%W"),
           date=TODAY.strftime("%d %B %Y")))


def generate_news():
    earliest = TODAY - timedelta(days=SHOW_LAST_X_DAYS_OF_NEWS)
    resp = requests.get(NEWS_URL.format(earliest.strftime("%Y-%m-%d")))
    topics = filter(lambda x: x["created_at"] >= earliest.isoformat(),
                    resp.json()["topics"])

    yield ("## Neuigkeiten")
    yield ("")
    if topics:
        for t in topics:
            yield (" - {state}[{fancy_title}]({BASE_URL}/t/{slug}/{id}) ({posts_count})".format(
                  BASE_URL=BASE_URL,
                  state="🔒 " if t["closed"] else "",
                  **t))

    else:
        yield ("_Keine Neuigkeiten_")

    yield ("")

    resp = requests.get(RECRUITING_URL).json()
    if "topics" in resp:
        yield ("### Aktuelle Gesuche")
        yield ("")
        for p in resp["topics"]:
            yield (" - [{title}]({BASE_URL}/t/{slug}/{id})".format(
                  BASE_URL=BASE_URL, **p))
        yield ("")


def generate_inis():
    resp = requests.get(VOTING_URL, headers={
        "X-Requested-With": "XMLHttpRequest",
        "accept": "application/json"})
    inis = resp.json()["content"]["initiatives"]

    vote_urgent = []
    to_vote = []
    discuss_urgent = []
    to_discuss = []
    ended_recently = []

    urgent = TODAY.date() + timedelta(days=SHOW_LAST_X_DAYS_OF_INIS + 1)
    recent = (TODAY.date() - timedelta(days=SHOW_LAST_X_DAYS_OF_INIS)).isoformat()

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


    yield ("## Initiativen")
    yield ("")
    yield ("### zur Abstimmung")

    if vote_urgent or to_vote:
        yield ("Aktuell stehen die folgenden Initiativen zur Abstimmung:")
        yield ("")
        for ini in vote_urgent:
            yield (" - **[{title}]({BASE_URL}/initiative/{id}-{slug})**, endet {weekday}".format(
                  BASE_URL=VOTING_BASE_URL,
                  weekday="HEUTE" if ini['end_of_this_phase'].day == TODAY.day else DAYS_OF_WEEK[ini['end_of_this_phase'].weekday()],
                  **ini))

        for ini in to_vote:
            yield (" - [{title}]({BASE_URL}/initiative/{id}-{slug})".format(
                  BASE_URL=VOTING_BASE_URL, **ini))

    else:
        # We show this every time to ensure People know it isn't left out
        yield ("_Es aktuell keine Initiativen zur Abstimmung_")


    if discuss_urgent or to_discuss:
        yield ("")
        yield ("### in Diskussion")
        for ini in discuss_urgent:
            yield (" - **[{title}]({BASE_URL}/initiative/{id}-{slug})**, endet {weekday}".format(
                  BASE_URL=VOTING_BASE_URL,
                  weekday="HEUTE" if ini['end_of_this_phase'].day == TODAY.day else DAYS_OF_WEEK[ini['end_of_this_phase'].weekday()],
                  **ini))

        for ini in to_discuss:
            yield (" - [{title}]({BASE_URL}/initiative/{id}-{slug})".format(
                  BASE_URL=VOTING_BASE_URL,**ini))

        yield ("")

    if ended_recently:
        yield ("### kürzlich abgestimmt")
        yield ("")
        for ini in ended_recently:
            yield (" - {icon} [{title}]({BASE_URL}/initiative/{id}-{slug})".format(
                  BASE_URL=VOTING_BASE_URL,
                  icon="👍" if ini['state'] == 'a' else "👎",
                  **ini))

        yield ("")
    yield ("")


def generate_events():
    today_iso = TODAY.isoformat()
    resp = requests.get(EVENTS_URL)
    events = []
    for t in resp.json()['topics']:
        topic = requests.get(BASE_URL + "/t/{slug}/{id}.json".format(**t)).json()
        if topic.get("event") and topic["event"]["start"] > today_iso:
            topic["event"]["start"] = dateutil.parser.parse(topic["event"]["start"])
            events.append(topic)


    yield ("## Veranstaltungen")
    yield ("")
    if events:
        for e in sorted(events, key=lambda x: x["event"]["start"]):
            location = ""
            if "location" in e and "name" in e["location"]:
                location = e["location"]["name"]

            yield (" - {date}: [{title}]({BASE_URL}/t/{slug}/{id}), {loc}".format(
                    BASE_URL=BASE_URL,
                    loc=location,
                    date=e["event"]["start"].strftime("%d.&nbsp;%b"),
                    **e)) 
    else:
        yield ("_keine Veranstaltungen geplant_")
    yield ("")
    yield ("""
Fehlt noch eine Veranstaltung? [Kündige diese passend auf dem Marktplatz an](https://marktplatz.bewegung.jetzt/t/veranstaltungen-fuer-iris-ankuendigen/11128?source_topic_id=2720) und sie wird mit aufgenommen!
""")


def generate_community():
    yield ("## Außerdem bewegt uns")
    yield ("")

    yield ("_CURATIERT. HIER EIN PAAR VORSCHLÄGE:_")
    for t in requests.get(TOP_URL).json()["topic_list"]["topics"]:
            yield (" - {state}[{fancy_title}]({BASE_URL}/t/{slug}/{id}) ({posts_count})".format(
                  BASE_URL=BASE_URL,
                  state="🔒 " if t["closed"] else "",
                  **t))



    yield ("")

    yield ("## Zitat der Woche")

    recent = (TODAY.date() - timedelta(days=SHOW_LAST_X_DAYS_OF_INIS)).isoformat()
    resp = requests.get(QUOTES_URL).json()
    new_quotes = sorted(filter(lambda x: x['created_at'] > recent,
                               resp["post_stream"]["posts"],),
                        reverse=True,
                        key=lambda p: ([x.get('count', 0) for x in p["actions_summary"]
                                        if x['id'] == 2] or (0,))[0])

    if new_quotes:
        yield ("_Vorlage der neuen Zitate, bei meisten Likes:_")
        for p in new_quotes[:3]:
            yield ("""
---
> {cooked}

> — eingereicht durch [{display_username}(@{username})]({BASE_URL}/u/{username})
""".format(BASE_URL=BASE_URL, **p))

    else:
        yield ("_Diese Woche ist uns kein lustiges DiB-Zitat zugespielt worden ☹._")
    yield ("")
    yield ("Du hast nen gutes Zitat? [Lass es uns wissen!](https://marktplatz.bewegung.jetzt/t/lustige-dib-zitate/10175)")
    yield ("")

def generate_footer():
    yield ("""
---

Iris wurde in dieser Woche zusammengestellt von dem besten [Ben](https://marktplatz.bewegung.jetzt/u/Ben/), der jubelnden [Johanna](https://marktplatz.bewegung.jetzt/u/Johanna/) und der leidenden [Lea](https://marktplatz.bewegung.jetzt/u/Leia/).

Du hast Anregungen, Fragen, Kekse? [Melde Dich gerne bei uns](https://marktplatz.bewegung.jetzt/t/neu-iris-die-woechtliche-zusammenfasssung-zum-sonntagsbrunch/10990)!
""")

def main():
    for fn in [generate_header, generate_news, generate_inis,
               generate_events, generate_community, generate_footer]:
        for p in fn():
            print(p)

if __name__ == '__main__':
    main()