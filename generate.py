#!/bin/env python

import requests
from datetime import datetime, date, timedelta
import dateutil.parser
import os
#import locale
from icalendar import Calendar 

if not "DC_TOKEN" in os.environ:
    print("Please specify the Discourse API token as DC_TOKEN!")
    exit(1)

DC_TOKEN = os.environ['DC_TOKEN']

#locale.setlocale(locale.LC_ALL,'de_DE.UTF-8')

SHOW_LAST_X_DAYS_OF_NEWS = 8
SHOW_LAST_X_DAYS_OF_INIS = 7

BASE_URL = "https://marktplatz.bewegung.jetzt"
NEWS_URL = BASE_URL + "/search.json?expanded=true&q=category:13 after:{} order:latest_topic"
EVENTS_URL = "https://bewegung.jetzt/events.ics"
RECRUITING_URL = BASE_URL + "/search.json?expanded=true&q=category:94 status:open after:2017-10-10 order:latest_topic"
PARTY_UPDATES_URL = BASE_URL + "/search.json?expanded=true&q=category:96 after:{} order:latest_topic"
TOP_URL = BASE_URL + "/top/weekly.json"
NEW_TK_URL = BASE_URL + "/search.json?expanded=true&q=category:169 status:open order:latest_topic"
SK_URL = BASE_URL + "/search.json?expanded=true&q=category:153 status:open after:2018-01-10 order:latest_topic"
SURVEYS_URL = BASE_URL + "/search.json?expanded=true&q=tags:umfrage,stimmungsbild,mitmachen status:open after:{} order:latest_topic"

QUOTES_URL = BASE_URL + "/t/fortsetzung-lustige-dib-zitate/24431/100.json"

def _today():
    today = datetime.today()
    if today.weekday() != 6:
        # If we aren't on Sunday, move to next Sunday
        today += timedelta(days=6 - today.weekday())
    return today

VOTING_BASE_URL = "https://abstimmen.bewegung.jetzt"
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

""".format(edition=_today().strftime("%G/%V"),
           date=_today().strftime("%d %B %Y")))


def generate_news():
    earliest = _today() - timedelta(days=SHOW_LAST_X_DAYS_OF_NEWS)
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

    resp = requests.get(RECRUITING_URL, headers={"Api-Username":"system","Api-Key":DC_TOKEN}).json()
    if "topics" in resp:
        yield ("### Aktuelle Gesuche")
        yield ("")
        for p in resp["topics"]:
            yield (" - [{title}]({BASE_URL}/t/{slug}/{id})".format(
                  BASE_URL=BASE_URL, **p))
        yield ("")

    resp = requests.get(PARTY_UPDATES_URL.format(earliest.strftime("%Y-%m-%d")), headers={"Api-Username":"system","Api-Key":DC_TOKEN}).json()
    if "topics" in resp:
        yield ("### Partei Updates")
        yield ("")
        yield("_Nur für Mitglieder und verifizierte Beweger\*innen einsehbar_. [Jetzt als Beweger\*in verifizieren](https://bewegung.jetzt/bewegerin-werden/).")
        yield("")
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

    urgent = _today().date() + timedelta(days=SHOW_LAST_X_DAYS_OF_INIS + 1)
    recent = (_today().date() - timedelta(days=SHOW_LAST_X_DAYS_OF_INIS)).isoformat()

    for ini in inis:
        if not ini['end_of_this_phase']: continue
        ini['end_of_this_phase'] = date(*map(int, ini['end_of_this_phase'].split("-"))) - timedelta(days=1)
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
                  weekday="HEUTE" if ini['end_of_this_phase'].day == _today().day else DAYS_OF_WEEK[ini['end_of_this_phase'].weekday()],
                  **ini))

        for ini in to_vote:
            yield (" - [{title}]({BASE_URL}/initiative/{id}-{slug})".format(
                  BASE_URL=VOTING_BASE_URL, **ini))

    else:
        # We show this every time to ensure People know it isn't left out
        yield ("_Es gibt aktuell keine Initiativen zur Abstimmung_")


    if discuss_urgent or to_discuss:
        yield ("")
        yield ("### in Diskussion")
        for ini in discuss_urgent:
            yield (" - **[{title}]({BASE_URL}/initiative/{id}-{slug})**, endet {weekday}".format(
                  BASE_URL=VOTING_BASE_URL,
                  weekday="HEUTE" if ini['end_of_this_phase'].day == _today().day else DAYS_OF_WEEK[ini['end_of_this_phase'].weekday()],
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
    today_iso = _today().isoformat()

    resp = requests.get(EVENTS_URL)
    cal = Calendar.from_ical(resp.text)


    yield ("## Veranstaltungen")
    yield ("")
    for evt in cal.walk(name="VEVENT"):
        title = evt.decoded("SUMMARY").decode("utf-8")
        date = evt.decoded("DTSTART")

        if today_iso >= date.isoformat():
            # happens between now and the day of this edition.
            continue

#        if evt.decoded("CATEGORIES", b"").decode("utf-8") == "Telefonkonferenz" or \
#            "call" in title.lower():
#            # we don't show telefon conferences
#            continue

        yield (" - {date}: [{title}]({URL}), {loc}".format(
                URL=evt.decoded("URL"),
                title=title,
                loc=evt.decoded("LOCATION", b"").decode("utf-8").replace(", Deutschland",""),
                date=evt.decoded("DTSTART").strftime("%d.&nbsp;%b")))
    yield ("")
    yield ("""
Alle Veranstaltungen sind von nun an auch auf der [Webseite zu finden](https://bewegung.jetzt/veranstaltungen/), ([iCal Feed](https://bewegung.jetzt/?ical=1)). Und so kannst [Du eine eigene Veranstaltung einreichen](https://marktplatz.bewegung.jetzt/t/eine-veranstaltung-auf-der-webseite-einreichen/21379).
""")


def generate_community():
    yield ("## Jetzt mitmischen")
    yield ("")
    yield ("_Einige der Themen sind nur für Mitglieder und verifizierte Beweger\*innen einsehbar_. [Jetzt als Beweger\*in verifizieren](https://bewegung.jetzt/bewegerin-werden/).")
    yield ("")
    resp = requests.get(NEW_TK_URL, headers={"Api-Username":"system","Api-Key":DC_TOKEN}).json()
    if "topics" in resp:
        for p in resp["topics"]:
            yield (" - [{title}]({BASE_URL}/t/{slug}/{id})".format(
                  BASE_URL=BASE_URL, **p))
        yield ("")

    resp = requests.get(SK_URL, headers={"Api-Username":"system","Api-Key":DC_TOKEN}).json()
    if "topics" in resp:
        for p in resp["topics"]:
            yield (" - [{title}]({BASE_URL}/t/{slug}/{id})".format(
                  BASE_URL=BASE_URL, **p))
        yield ("")

    earliest = _today() - timedelta(days=SHOW_LAST_X_DAYS_OF_NEWS*2)

    resp = requests.get(SURVEYS_URL.format(earliest.strftime("%Y-%m-%d")), headers={"Api-Username":"system","Api-Key":DC_TOKEN}).json()
    if "topics" in resp:
        for p in resp["topics"]:
            yield (" - [{title}]({BASE_URL}/t/{slug}/{id})".format(
                  BASE_URL=BASE_URL, **p))
        yield ("")
    yield ("")
    yield ("## Außerdem bewegt uns")
    yield ("")

    yield ("_KURATIERT. HIER EIN PAAR VORSCHLÄGE:_")
    for t in requests.get(TOP_URL).json()["topic_list"]["topics"]:
            yield (" - {state}[{fancy_title}]({BASE_URL}/t/{slug}/{id}) ({posts_count})".format(
                  BASE_URL=BASE_URL,
                  state="🔒 " if t["closed"] else "",
                  **t))


    yield ("")

    yield ("## ❤️ Danke ❤️")

    yield ("_Hier ein Danke eintragen, falls es eines gibt diese Woche._")

    yield ("")

    yield ("## Zitat der Woche")

    recent = (_today().date() - timedelta(days=SHOW_LAST_X_DAYS_OF_INIS)).isoformat()
    resp = requests.get(QUOTES_URL, headers={"Api-Username":"system","Api-Key":DC_TOKEN}).json()
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
    yield ("Du hast ein gutes Zitat? [Dann reiche es hier ein.](https://marktplatz.bewegung.jetzt/t/lustige-dib-zitate/10175)")
    yield ("")

def generate_footer():
    yield ("""
---

Iris wurde in dieser Woche zusammengestellt von [Guido](https://marktplatz.bewegung.jetzt/u/Guido/) und [Michael](https://marktplatz.bewegung.jetzt/u/MichaelVoss/).

Du hast Anregungen oder Fragen? [Melde Dich gerne bei uns](https://marktplatz.bewegung.jetzt/t/neu-iris-die-woechtliche-zusammenfasssung-zum-sonntagsbrunch/10990)!
""")

def main():
    for fn in [generate_header,
               generate_news,
               generate_inis,
               generate_events, 
               generate_community,
               generate_footer]:
        for p in fn():
            print(p)

if __name__ == '__main__':
    main()
