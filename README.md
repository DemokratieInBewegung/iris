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
