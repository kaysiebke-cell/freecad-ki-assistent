import re
import FreeCAD as App
import FreeCADGui as Gui

try:
    from PySide6 import QtCore, QtWidgets, QtGui
except ImportError:
    from PySide2 import QtCore, QtWidgets, QtGui


# ── Syntax-Highlighter ───────────────────────────────────────────────────────
class PythonHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []

        def add(pattern, color, bold=False, italic=False):
            fmt = QtGui.QTextCharFormat()
            fmt.setForeground(QtGui.QColor(color))
            if bold:   fmt.setFontWeight(QtGui.QFont.Bold)
            if italic: fmt.setFontItalic(True)
            self.rules.append((re.compile(pattern), fmt))

        add(r'\b(False|None|True|and|as|assert|async|await|break|class|'
            r'continue|def|del|elif|else|except|finally|for|from|global|'
            r'if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|'
            r'try|while|with|yield)\b',                   "#569cd6", bold=True)
        add(r'\bself\b',                                  "#9cdcfe")
        add(r'\b(App|Gui|Part|PartDesign|Sketcher|'
            r'Vector|Placement|Rotation|doc)\b',          "#9cdcfe", bold=True)
        add(r'\b(abs|all|any|bool|dict|enumerate|float|'
            r'int|len|list|map|max|min|print|range|'
            r'round|set|sorted|str|sum|tuple|type|zip)\b',"#569cd6")
        add(r'"[^"\\]*(\\.[^"\\]*)*"',                   "#ce9178")
        add(r"'[^'\\]*(\\.[^'\\]*)*'",                   "#ce9178")
        add(r'#[^\n]*',                                   "#6a9955", italic=True)
        add(r'\b[0-9]+\.?[0-9]*\b',                      "#b5cea8")
        add(r'(?<=def )\w+',                              "#dcdcaa")
        add(r'(?<=class )\w+',                            "#dcdcaa")

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for m in pattern.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), fmt)


# ── Haupt-Widget ─────────────────────────────────────────────────────────────
class FreeCAD_MultiAI_Panel(QtWidgets.QWidget):

    SYSTEM_PROMPT = (
        "Du bist ein FreeCAD 1.1.1 Python-Experte. "
        "Antworte NUR mit reinem Python-Code, KEINE Erklärungen, KEINE Markdown-Zäune.\n\n"
        "PFLICHTREGELN:\n"
        "- Boolesche Ops NUR so:\n"
        "    result = a.cut(b)   # Subtraktion\n"
        "    result = a.fuse(b)  # Vereinigung\n"
        "- NIEMALS -= oder += auf Part-Objekten\n"
        "- Nach jeder booleschen Op das Ergebnis ins Dokument schreiben:\n"
        "    obj = doc.addObject('Part::Feature', 'Name')\n"
        "    obj.Shape = result\n"
        "- Maße immer als float: 40.0 nicht 40mm\n"
        "- Kein .Support, kein saveCopy, kein export\n\n"
        "BEISPIEL – Würfel 40mm mit Bohrung 10mm Durchmesser:\n"
        "import Part\n"
        "wuerfel  = Part.makeBox(40.0, 40.0, 40.0)\n"
        "zylinder = Part.makeCylinder(5.0, 40.0, App.Vector(20.0, 20.0, 0.0), App.Vector(0, 0, 1))\n"
        "ergebnis = wuerfel.cut(zylinder)\n"
        "obj = doc.addObject('Part::Feature', 'WuerfelMitBohrung')\n"
        "obj.Shape = ergebnis\n"
        "doc.recompute()\n"
    )

    def __init__(self):
        super().__init__()
        self.openrouter_key = "DEIN_KEY_HIER"
        self.worker = None
        self._build_ui()
        self._refresh_models()

    # ── UI ───────────────────────────────────────────────────────────────────
    def _build_ui(self):
        g = QtWidgets.QGridLayout(self)
        g.setSpacing(6)
        g.setContentsMargins(8, 8, 8, 8)

        # Quelle
        g.addWidget(QtWidgets.QLabel("KI-Quelle:"), 0, 0, 1, 2)
        self.source_box = QtWidgets.QComboBox()
        self.source_box.addItems(["Ollama (Lokal)", "OpenRouter (Cloud)"])
        self.source_box.currentIndexChanged.connect(self._refresh_models)
        g.addWidget(self.source_box, 1, 0, 1, 2)

        # Modell + Refresh
        self.model_box = QtWidgets.QComboBox()
        g.addWidget(self.model_box, 2, 0)
        btn_ref = QtWidgets.QPushButton("🔄")
        btn_ref.setFixedWidth(35)
        btn_ref.clicked.connect(self._refresh_models)
        g.addWidget(btn_ref, 2, 1)

        # Verbindungsstatus
        row_conn = QtWidgets.QHBoxLayout()
        self.conn_dot   = QtWidgets.QLabel("●")
        self.conn_dot.setFixedWidth(18)
        self.conn_info  = QtWidgets.QLabel("Nicht geprüft")
        self.conn_info.setStyleSheet("color:gray; font-size:11px;")
        row_conn.addWidget(self.conn_dot)
        row_conn.addWidget(self.conn_info)
        row_conn.addStretch()
        g.addLayout(row_conn, 3, 0, 1, 2)

        # Arbeitsbereich-Anzeige
        wb_row = QtWidgets.QHBoxLayout()
        wb_row.addWidget(QtWidgets.QLabel("Arbeitsbereich:"))
        self.wb_label = QtWidgets.QLabel("…")
        self.wb_label.setStyleSheet(
            "color:#dcdcaa; font-weight:bold; font-size:11px;")
        wb_row.addWidget(self.wb_label)
        wb_row.addStretch()
        g.addLayout(wb_row, 4, 0, 1, 2)

        # Eingabe
        self.input_text = QtWidgets.QTextEdit()
        self.input_text.setPlaceholderText("Bauteil beschreiben …")
        self.input_text.setFixedHeight(80)
        g.addWidget(self.input_text, 4, 0, 1, 2)

        # Generieren-Button
        self.btn_ask = QtWidgets.QPushButton("⚙ Code generieren")
        self.btn_ask.setStyleSheet(
            "background-color:#444;color:white;padding:8px;font-weight:bold;")
        self.btn_ask.clicked.connect(self._handle_request)
        g.addWidget(self.btn_ask, 5, 0, 1, 2)

        # Fortschrittsbalken
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        self.progress.setVisible(False)
        g.addWidget(self.progress, 6, 0, 1, 2)

        # Statuszeile
        self.status_lbl = QtWidgets.QLabel("Bereit.")
        self.status_lbl.setStyleSheet("color:gray; font-size:11px; padding:2px 0;")
        g.addWidget(self.status_lbl, 7, 0, 1, 2)

        # Code-Anzeige
        self.code_display = QtWidgets.QPlainTextEdit()
        self.code_display.setStyleSheet(
            "background-color:#1e1e1e; color:#a9b7c6; "
            "font-family:'Monospace'; font-size:12px;")
        PythonHighlighter(self.code_display.document())
        g.addWidget(self.code_display, 8, 0, 1, 2)
        g.setRowStretch(8, 1)

        # Anwenden-Button
        self.btn_run = QtWidgets.QPushButton("▶ In FreeCAD anwenden")
        self.btn_run.setFixedHeight(40)
        self.btn_run.setStyleSheet(
            "background-color:#2e7d32;color:white;font-weight:bold;")
        self.btn_run.clicked.connect(self._execute_code)
        g.addWidget(self.btn_run, 9, 0, 1, 2)

    # ── Verbindungsanzeige ───────────────────────────────────────────────────
    def _set_conn(self, ok, text):
        color = "#4caf50" if ok else "#f44336"
        self.conn_dot.setStyleSheet(f"color:{color}; font-size:14px;")
        self.conn_info.setText(text)
        self.conn_info.setStyleSheet(f"color:{color}; font-size:11px;")

    def _set_busy(self, busy, msg=""):
        self.progress.setVisible(busy)
        self.btn_ask.setEnabled(not busy)
        self.btn_run.setEnabled(not busy)
        self.status_lbl.setText(msg if msg else ("Bereit." if not busy else ""))
        QtWidgets.QApplication.processEvents()

    # ── Modelle laden ────────────────────────────────────────────────────────
    def _refresh_models(self):
        import requests
        self.model_box.clear()
        if "Ollama" in self.source_box.currentText():
            self._set_conn(False, "Verbinde mit Ollama …")
            QtWidgets.QApplication.processEvents()
            try:
                r = requests.get("http://localhost:11434/api/tags", timeout=3)
                models = [m["name"] for m in r.json().get("models", [])]
                self.model_box.addItems(models or ["(keine Modelle)"])
                self._set_conn(bool(models), f"Ollama: {len(models)} Modell(e)")
            except requests.exceptions.ConnectionError:
                self.model_box.addItem("Ollama offline")
                self._set_conn(False, "Ollama nicht erreichbar")
            except Exception as e:
                self.model_box.addItem("Fehler")
                self._set_conn(False, str(e))
        else:
            self.model_box.addItems([
                "anthropic/claude-3.5-sonnet",
                "openai/gpt-4o-mini",
                "mistralai/mistral-7b-instruct",
            ])
            if self.openrouter_key.startswith("DEIN"):
                self._set_conn(False, "Kein API-Key gesetzt!")
            else:
                try:
                    r = requests.get(
                        "https://openrouter.ai/api/v1/auth/key",
                        headers={"Authorization": f"Bearer {self.openrouter_key}"},
                        timeout=5)
                    if r.status_code == 200:
                        credits = r.json().get("data", {}).get("limit_remaining", "?")
                        self._set_conn(True, f"OpenRouter OK | Guthaben: {credits}")
                    else:
                        self._set_conn(False, f"OpenRouter Fehler {r.status_code}")
                except Exception as e:
                    self._set_conn(False, f"Nicht erreichbar: {e}")

    # ── Anfrage ──────────────────────────────────────────────────────────────
    def _build_system_prompt(self):
        """Erstellt den System-Prompt mit aktuellem Arbeitsbereich."""
        try:
            wb_name = Gui.activeWorkbench().__class__.__name__
        except Exception:
            wb_name = "Unbekannt"

        # Anzeige im Panel aktualisieren
        labels = {
            "PartDesignWorkbench": "Part Design",
            "PartWorkbench":       "Part",
            "MeshWorkbench":       "Mesh",
        }
        self.wb_label.setText(labels.get(wb_name, wb_name))

        wb_hints = {
            "PartDesignWorkbench": (
                "Du arbeitest im PART DESIGN Arbeitsbereich.\n"
                "PFLICHT: Immer Body → Skizze → Pad/Pocket verwenden. NIEMALS Part.makeBox!\n\n"
                "VOLLSTÄNDIGES BEISPIEL – Würfel 40mm mit Bohrung 10mm:\n"
                "  import Sketcher\n"
                "  # 1. Body anlegen\n"
                "  body = doc.addObject('PartDesign::Body', 'Body')\n"
                "  # 2. Skizze für Grundfläche (XY-Ebene)\n"
                "  sk_base = body.newObject('Sketcher::SketchObject', 'Sketch_Base')\n"
                "  sk_base.Support = (doc.getObject('XY_Plane'), [''])\n"
                "  sk_base.MapMode = 'FlatFace'\n"
                "  sk_base.addGeometry(Part.LineSegment(App.Vector(0,0,0),  App.Vector(40,0,0)))\n"
                "  sk_base.addGeometry(Part.LineSegment(App.Vector(40,0,0), App.Vector(40,40,0)))\n"
                "  sk_base.addGeometry(Part.LineSegment(App.Vector(40,40,0),App.Vector(0,40,0)))\n"
                "  sk_base.addGeometry(Part.LineSegment(App.Vector(0,40,0), App.Vector(0,0,0)))\n"
                "  doc.recompute()\n"
                "  # 3. Pad (Extrusion)\n"
                "  pad = body.newObject('PartDesign::Pad', 'Pad')\n"
                "  pad.Profile = sk_base\n"
                "  pad.Length = 40.0\n"
                "  doc.recompute()\n"
                "  # 4. Skizze für Bohrung (oben auf dem Pad)\n"
                "  sk_hole = body.newObject('Sketcher::SketchObject', 'Sketch_Hole')\n"
                "  sk_hole.Support = (pad, ['Face6'])\n"
                "  sk_hole.MapMode = 'FlatFace'\n"
                "  sk_hole.addGeometry(Part.Circle(App.Vector(20,20,0), App.Vector(0,0,1), 5.0))\n"
                "  doc.recompute()\n"
                "  # 5. Pocket (Bohrung)\n"
                "  pocket = body.newObject('PartDesign::Pocket', 'Pocket')\n"
                "  pocket.Profile = sk_hole\n"
                "  pocket.Length = 40.0\n"
                "  doc.recompute()\n"
            ),
            "PartWorkbench": (
                "Du arbeitest im PART Arbeitsbereich.\n"
                "Nutze Part-Primitives und boolesche Operationen:\n"
                "  Part.makeBox / makeCylinder / makeSphere\n"
                "  result = a.cut(b)  /  a.fuse(b)\n"
                "  obj = doc.addObject('Part::Feature','Name'); obj.Shape = result\n"
            ),
            "MeshWorkbench": (
                "Du arbeitest im MESH Arbeitsbereich.\n"
                "Nutze Mesh-Operationen mit import Mesh.\n"
            ),
        }
        wb_hint = wb_hints.get(wb_name,
            f"Aktiver Arbeitsbereich: {wb_name}. "
            "Passe den Code entsprechend an.\n")

        return (
            self.SYSTEM_PROMPT +
            f"\nAKTIVER ARBEITSBEREICH: {wb_name}\n" +
            wb_hint
        )

    def _handle_request(self):
        prompt = self.input_text.toPlainText().strip()
        if not prompt:
            self.status_lbl.setText("⚠ Bitte eine Beschreibung eingeben.")
            return
        self._set_busy(True, "⏳ KI denkt nach …")
        source = self.source_box.currentText()
        model  = self.model_box.currentText()

        self.worker = QtCore.QThread()
        self._task   = _APIWorker(source, model, prompt, self.openrouter_key,
                                  self._build_system_prompt())
        self._task.moveToThread(self.worker)
        self.worker.started.connect(self._task.run)
        self._task.done.connect(self._on_result)
        self._task.error.connect(self._on_error)
        self._task.done.connect(self.worker.quit)
        self._task.error.connect(self.worker.quit)
        self.worker.start()

    def _on_result(self, code):
        self.code_display.setPlainText(self._clean(code))
        self._set_busy(False, "✅ Code empfangen – bitte prüfen, dann anwenden.")

    def _on_error(self, msg):
        self.code_display.setPlainText(f"# Fehler:\n# {msg}")
        self._set_busy(False, f"❌ {msg}")
        self._set_conn(False, "Verbindungsfehler")

    # ── Code bereinigen ──────────────────────────────────────────────────────
    def _clean(self, code: str) -> str:
        # 1. Markdown-Zäune
        code = re.sub(r'```[\w]*', '', code).strip()

        # 2. Prosazeilen entfernen
        result = []
        for line in code.splitlines():
            s = line.strip()
            if not s:
                result.append('')
                continue
            is_code = (
                line[0] in (' ', '\t')
                or s.startswith('#')
                or re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*\s*[\(=\[\{:\+\-\*]', s)
                or re.match(
                    r'^(import|from|def|class|if|elif|else|for|while|'
                    r'try|except|finally|with|return|raise|pass|break|'
                    r'continue|print|doc|App|Gui|Part|math|Vector|'
                    r'Placement|Rotation|True|False|None)\b', s)
            )
            if is_code:
                result.append(line)

        code = '\n'.join(result).strip()

        # 3. Falsche Part-Operatoren korrigieren
        code = re.sub(r'^(\s*)(\w+)\s*-=\s*(.+)$',
                      r'\1\2 = \2.cut(\3)',  flags=re.MULTILINE, string=code)
        code = re.sub(r'^(\s*)(\w+)\s*\+=\s*(.+)$',
                      r'\1\2 = \2.fuse(\3)', flags=re.MULTILINE, string=code)
        code = re.sub(r'^(\s*)(\w+)\s*\*=\s*(.+)$',
                      r'\1\2 = \2.common(\3)', flags=re.MULTILINE, string=code)
        return code

    # ── Code ausführen ───────────────────────────────────────────────────────
    def _execute_code(self):
        code = self._clean(self.code_display.toPlainText())
        if not code or code.startswith("#"):
            self.status_lbl.setText("⚠ Kein ausführbarer Code vorhanden.")
            return
        if App.ActiveDocument is None:
            App.newDocument("KI_Konstruktion")
        self._set_busy(True, "▶ Führe Code aus …")
        try:
            import Part, Sketcher, math
            ns = {
                "App": App, "Gui": Gui, "Part": Part,
                "Sketcher": Sketcher, "math": math,
                "doc": App.ActiveDocument,
                "Vector": App.Vector,
                "Placement": App.Placement,
                "Rotation": App.Rotation,
            }
            exec(compile(code, "<KI-Code>", "exec"), ns)
            App.ActiveDocument.recompute()
            Gui.updateGui()
            Gui.SendMsgToActiveView("ViewFit")
            self._set_busy(False, "✅ Erfolgreich angewendet.")
        except SyntaxError as e:
            self._set_busy(False, f"❌ Syntaxfehler Zeile {e.lineno}: {e.msg}")
            QtWidgets.QMessageBox.critical(
                None, "Syntaxfehler", f"Zeile {e.lineno}: {e.msg}\n\n{e.text}")
        except Exception as e:
            self._set_busy(False, f"❌ Laufzeitfehler: {e}")
            QtWidgets.QMessageBox.critical(
                None, "Laufzeit Fehler", f"Details:\n{str(e)}")


# ── Worker-Thread ────────────────────────────────────────────────────────────
class _APIWorker(QtCore.QObject):
    done  = QtCore.Signal(str)
    error = QtCore.Signal(str)

    def __init__(self, source, model, prompt, key, system):
        super().__init__()
        self.source = source
        self.model  = model
        self.prompt = prompt
        self.key    = key
        self.system = system

    def run(self):
        import requests
        try:
            if "Ollama" in self.source:
                r = requests.post(
                    "http://localhost:11434/api/generate",
                    json={"model": self.model,
                          "prompt": f"{self.system}\n\nAufgabe: {self.prompt}",
                          "stream": False},
                    timeout=300)
                r.raise_for_status()
                self.done.emit(r.json().get("response", ""))
            else:
                r = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.key}",
                             "Content-Type": "application/json"},
                    json={"model": self.model,
                          "messages": [
                              {"role": "system", "content": self.system},
                              {"role": "user",   "content": self.prompt}
                          ]},
                    timeout=60)
                r.raise_for_status()
                self.done.emit(r.json()["choices"][0]["message"]["content"])
        except Exception as e:
            self.error.emit(str(e))


# ── Dock einbinden ───────────────────────────────────────────────────────────
def add_ai_panel():
    mw = Gui.getMainWindow()
    for child in mw.findChildren(QtWidgets.QDockWidget):
        if child.windowTitle() == "KI Multi-Source Assistent":
            mw.removeDockWidget(child)
            child.deleteLater()
    panel = FreeCAD_MultiAI_Panel()
    dock  = QtWidgets.QDockWidget("KI Multi-Source Assistent")
    dock.setWidget(panel)
    mw.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

if __name__ == "__main__":
    add_ai_panel()