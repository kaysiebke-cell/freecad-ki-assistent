# FreeCAD KI-Assistent

Ein KI-gestütztes Dock-Panel für FreeCAD 1.1.1, das Python-Code für 3D-Bauteile direkt aus einer Textbeschreibung generiert und ausführt.

![FreeCAD Version](https://img.shields.io/badge/FreeCAD-1.1.1-blue)
![Python](https://img.shields.io/badge/Python-3.x-yellow)
![Lizenz](https://img.shields.io/badge/Lizenz-MIT-green)

---

## Features

- **KI-Code-Generierung** – Bauteil in natürlicher Sprache beschreiben, fertigen Python-Code erhalten
- **Zwei KI-Quellen** – Lokales Ollama-Modell oder OpenRouter Cloud
- **Arbeitsbereich-Erkennung** – Erkennt automatisch ob Part oder Part Design aktiv ist und generiert den passenden Code
- **Syntax-Highlighting** – Code-Anzeige mit Python-Farbgebung im VS Code Dark+ Stil
- **Automatischer Code-Patcher** – Korrigiert fehlerhafte boolesche Operatoren selbstständig
- **Verbindungsanzeige** – Zeigt ob Ollama läuft oder der OpenRouter-Key gültig ist
- **Direkte Ausführung** – Generierten Code mit einem Klick in FreeCAD anwenden

---

## Voraussetzungen

- FreeCAD 1.1.1
- Python-Paket `requests` im FreeCAD-Python-Pfad installiert
- Für lokale KI: [Ollama](https://ollama.com) mit einem installierten Modell
- Für Cloud-KI: API-Key von [OpenRouter](https://openrouter.ai)

---

## Installation

1. Datei `KI_Konstruktions_Assistent.py` herunterladen
2. In FreeCAD: **Makro → Makros… → Speicherort öffnen**
3. Datei in den Makro-Ordner kopieren
4. In FreeCAD: **Makro → Makros… → Skript auswählen → Ausführen**

Das Panel erscheint als Dock auf der rechten Seite.

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

## Bekannte Einschränkungen

- Kleine lokale Modelle (7b) erzeugen manchmal unvollständigen Code
- Part Design Skizzen-Workflow ist komplexer als Part-Primitives – größere Modelle empfohlen
- Der automatische Code-Patcher deckt die häufigsten Fehler ab, kann aber nicht alle KI-Fehler korrigieren

---

## Mitwirkende

Entwickelt von **kaysiebke-cell** mit Unterstützung von Claude (Anthropic).

---

## Lizenz

MIT – frei verwendbar und veränderbar.
