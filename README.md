# digest
Ein wöchtlicher Rück- und Ausblick über die Vorgänge in DEMOKRATIE IN BEWEGUNG


## Setup

Wir nutzen ein automatisches Script um die wöchentliche Ausgabe zu erstellen. Um dieses Ausführen zu können, brauchst du _Python_ (in Version 3.5 oder höher) mit `virtualenv` auf deinem System. Danach führe folgendes aus:

### Einmalige Installation

```
virtualenv .
source bin/activate
pip install -r requirements.txt
```

### Virtuelle Umgebung

Um das script ausführen zu können, musst du dies immer aus der "virtuellen Umgebung" aus ausrufen. Um in die Virtuelle Umgebung zu wechseln, führe

```
source bin/activate
```

aus.

## Neue Edition erstellen

Innerhalb der virtuellen Umgebung (siehe oben), das folgende Kommando ausführen um die neue Edition mit dem aktuellen Datum zu generieren:

```
python generate.py > > _posts/`date +%Y-%m-%d-DiB-digest-%Y.%W.md`
```

# Writer's Guideline

Checkliste vor jedem Abschicken:

1. Wir gendern durchgehend
2. Hervorhebung per Fett-Druck, nicht kursiv oder unterstrich!
3. Keine Links in Überschriften
4. Veranstaltungen nur für die nächsten 30 Tage, ausgenommen sind Landes- und Bundesparteitage
5. 


# ToDo's

- [ ] Diese Woche auf Marktplatz bekannt geben, nächste Woche über Newsletter

## Webseite:

 - [ ] das Impressum muss noch gemacht werden, insb. uns Kurator/innen dort ausführen
 - [ ] das Seiten-Menu geht noch nicht gescheit auf mobile.
 - [ ] einen neuen Eintrag hinzufügen und sehen ob der (aktuell nicht angezeigte) "Vorherige Ausgabe"-Link funzt
 - [ ] RSS, damit Leute auch mit-nicht-per-email abonnieren können
 - [ ] Social-Media-Embed-Meta-Data (damit es bei FB, Twitter und auf dem Marktplatz nett angezeigt wird)
 - [ ] Headline-Stufe 3 nicht fett
 - [ ] Ausgaben-Format: 2017/45

## Mailer:

 - [ ] Headline-Stufe 3 nicht fett
 - [ ] Titel-Zeile “Diese Woche bei DiB”
 - [ ] Ausgaben-Format: 2017/45

## Editionen/Script:

- [ ] Gendern
- [*] “Neuigkeiten & Bekanntmachung” → “Neuigkeiten”
- [*] Wir-suchen als Unterpunkt in Neuigkeiten
- [ ] Ausgaben-Format: 2017/45
- [*] Sabine’s-Link funktionierte nicht
