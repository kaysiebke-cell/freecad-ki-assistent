# FreeCAD KI-Assistent

Ein KI-gestütztes Dock-Panel für FreeCAD 1.1.1, das Python-Code für 3D-Bauteile direkt aus einer Textbeschreibung generiert und ausführt.

![FreeCAD Version](https://img.shields.io/badge/FreeCAD-1.1.1-blue)
![Python](https://img.shields.io/badge/Python-3.x-yellow)
![Lizenz](https://img.shields.io/badge/Lizenz-MIT-green)
![Sprachen](https://img.shields.io/badge/Sprachen-DE%20%7C%20EN%20%7C%20FR%20%7C%20IT%20%7C%20ES-orange)

---

![Screenshot – FreeCAD KI-Assistent](DEIN_BILD_LINK_HIER)
> *Würfel mit zentraler Bohrung – generiert und angewendet mit einem Klick*

---

## Features

- **KI-Code-Generierung** – Bauteil in natürlicher Sprache beschreiben, fertigen Python-Code erhalten
- **Zwei KI-Quellen** – Lokales Ollama-Modell oder OpenRouter Cloud
- **Arbeitsbereich-Erkennung** – Erkennt automatisch ob Part oder Part Design aktiv ist und generiert den passenden Code
- **Syntax-Highlighting** – Code-Anzeige mit Python-Farbgebung im VS Code Dark+ Stil
- **Automatischer Code-Patcher** – Korrigiert fehlerhafte boolesche Operatoren selbstständig
- **Verbindungsanzeige** – Zeigt ob Ollama läuft oder der OpenRouter-Key gültig ist
- **Direkte Ausführung** – Generierten Code mit einem Klick in FreeCAD anwenden
- **Inline-Rechtschreibprüfung** – Fehler werden direkt im Eingabefeld farbig hervorgehoben (via hunspell)
- **Korrekturvorschläge** – Rechtsklick auf ein markiertes Wort zeigt bis zu 7 Verbesserungsvorschläge
- **Fachbegriffe ignorieren** – Technische Begriffe können per Rechtsklick für die Sitzung ausgeblendet werden
- **Frei skalierbares Panel** – Breite des Dock-Fensters ist frei anpassbar
- **Automatische Mehrsprachigkeit** – Sprache wird automatisch aus der FreeCAD-Einstellung erkannt (DE, EN, FR, IT, ES u.v.m.)

---

## Unterstützte Sprachen

Die Sprache der Benutzeroberfläche und der Rechtschreibprüfung wird automatisch aus der FreeCAD-Spracheinstellung übernommen – keine manuelle Konfiguration nötig.

| Sprache | Code | Hunspell-Paket |
|---|---|---|
| Deutsch | `de` | `hunspell-de-de` |
| Englisch | `en` | `hunspell-en-us` |
| Französisch | `fr` | `hunspell-fr` |
| Italienisch | `it` | `hunspell-it` |
| Spanisch | `es` | `hunspell-es` |

Die FreeCAD-Sprache lässt sich unter **Bearbeiten → Einstellungen → Allgemein → Sprache** einstellen.

---

## Voraussetzungen

- FreeCAD 1.1.1
- Python-Paket `requests` im FreeCAD-Python-Pfad installiert
- Für lokale KI: [Ollama](https://ollama.com) mit einem installierten Modell
- Für Cloud-KI: API-Key von [OpenRouter](https://openrouter.ai)
- Für Rechtschreibprüfung: `hunspell` mit dem passenden Sprachwörterbuch

---

## Installation

### 1. Skript einrichten

1. Datei `KI_Konstruktions_Assistent.py` herunterladen
2. In FreeCAD: **Makro → Makros… → Speicherort öffnen**
3. Datei in den Makro-Ordner kopieren
4. In FreeCAD: **Makro → Makros… → Skript auswählen → Ausführen**

Das Panel erscheint als Dock auf der rechten Seite.

### 2. Rechtschreibprüfung einrichten (einmalig)

Wörterbuch für die gewünschte Sprache installieren:

```bash
# Deutsch
sudo apt install hunspell hunspell-de-de

# Englisch
sudo apt install hunspell hunspell-en-us

# Französisch
sudo apt install hunspell hunspell-fr

# Italienisch
sudo apt install hunspell hunspell-it

# Spanisch
sudo apt install hunspell hunspell-es
```

Die Rechtschreibprüfung ist danach automatisch aktiv – kein weiterer Schritt nötig.

---

## Konfiguration

Die Datei einmalig öffnen und den eigenen OpenRouter-Key eintragen:

```python
self.openrouter_key = "sk-or-v1-DEIN_KEY_HIER"
```

Für Ollama ist kein Key nötig – einfach Ollama starten und ein Modell laden:

```bash
ollama run qwen2.5-coder:7b
```

---

## Verwendung der Rechtschreibprüfung

Fehler werden beim Tippen sofort farbig hinterlegt.  
**Rechtsklick** auf ein markiertes Wort öffnet das Korrekturmenü:

- `📝 Vorschläge für „Wort":` – bis zu 7 Korrekturvorschläge anklicken
- `🚫 Wort ignorieren` – Fachbegriffe für die aktuelle Sitzung ausblenden

---

## Tipps für gute Ergebnisse

Je genauer die Beschreibung, desto besser der Code.

**Gutes Beispiel:**

```
Erstelle ein Python-Skript für FreeCAD: Erzeuge einen Würfel (Part.makeBox)
mit 40x40x40 mm. Platziere eine zentrale Bohrung (Zylinder) mit 10 mm
Durchmesser (Radius 5 mm), die den Würfel komplett auf der Z-Achse
durchdringt. Zentriere den Zylinder auf X=20 und Y=20. Führe eine
Boolesche Subtraktion durch und aktualisiere das Dokument.
```

**Schlechtes Beispiel:**

```
Mach einen Würfel mit Loch.
```

---

## Getestete Modelle

| Modell | Quelle | Bewertung |
|---|---|---|
| `qwen2.5-coder:7b` | Ollama lokal | ⭐⭐⭐ Grundlegende Teile funktionieren |
| `qwen2.5-coder:14b` | Ollama lokal | ⭐⭐⭐⭐ Deutlich zuverlässiger |
| `claude-3.5-sonnet` | OpenRouter | ⭐⭐⭐⭐⭐ Beste Ergebnisse |
| `gpt-4o-mini` | OpenRouter | ⭐⭐⭐⭐ Gut für einfache Bauteile |

---

## Unterstützte Arbeitsbereiche

| Arbeitsbereich | Generierter Code-Stil |
|---|---|
| Part | `Part.makeBox`, `cut()`, `fuse()` |
| Part Design | `Body → Sketch → Pad / Pocket` |
| Mesh | `import Mesh` |

---

## Bekannte Einschränkungen

- Kleine lokale Modelle (7b) erzeugen manchmal unvollständigen Code
- Part Design Skizzen-Workflow ist komplexer als Part-Primitives – größere Modelle empfohlen
- Der automatische Code-Patcher deckt die häufigsten Fehler ab, kann aber nicht alle KI-Fehler korrigieren
- Rechtschreibprüfung erkennt technische Begriffe wie `Part.makeBox` nicht als Fehler
- Sprachen ohne hunspell-Wörterbuch laufen ohne Rechtschreibprüfung, alle anderen Funktionen bleiben verfügbar

---

## Mitwirkende

Entwickelt von **kaysiebke-cell** mit Unterstützung von Claude (Anthropic).

---

## Lizenz

MIT – frei verwendbar und veränderbar.

---

## Lizenz

MIT – frei verwendbar und veränderbar.
