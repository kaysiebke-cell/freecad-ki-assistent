import re
import FreeCAD as App
import FreeCADGui as Gui

try:
    from PySide6 import QtCore, QtWidgets, QtGui
except ImportError:
    from PySide2 import QtCore, QtWidgets, QtGui


# ── Sprache aus FreeCAD erkennen ─────────────────────────────────────────────
def _detect_language() -> str:
    try:
        lang = App.ParamGet(
            "User parameter:BaseApp/Preferences/General"
        ).GetString("Language", "en")
        return lang[:2].lower()   # "de_DE" → "de",  "en_US" → "en"
    except Exception:
        return "en"

LANG = _detect_language()

# hunspell-Wörterbuch je Sprache
LANG_TO_DICT = {
    "de": "de_DE", "en": "en_US", "fr": "fr_FR",
    "it": "it_IT", "es": "es_ES", "pt": "pt_PT",
    "nl": "nl_NL", "pl": "pl_PL", "ru": "ru_RU",
}
SPELL_LANG = LANG_TO_DICT.get(LANG, "en_US")

# ── Übersetzungen ─────────────────────────────────────────────────────────────
_T = {
    "de": {
        "source_label":    "KI-Quelle:",
        "ollama":          "Ollama (Lokal)",
        "openrouter":      "OpenRouter (Cloud)",
        "not_checked":     "Nicht geprüft",
        "workbench":       "Arbeitsbereich:",
        "spell_active":    "🟢 Rechtschreibprüfung aktiv ({})",
        "spell_missing":   "🔴 hunspell nicht verfügbar  →  sudo apt install hunspell-{}",
        "placeholder":     "Bauteil beschreiben …",
        "btn_generate":    "⚙ Code generieren",
        "btn_apply":       "▶ In FreeCAD anwenden",
        "ready":           "Bereit.",
        "thinking":        "⏳ KI denkt nach …",
        "code_received":   "✅ Code empfangen – bitte prüfen, dann anwenden.",
        "applied":         "✅ Erfolgreich angewendet.",
        "no_input":        "⚠ Bitte eine Beschreibung eingeben.",
        "no_code":         "⚠ Kein ausführbarer Code vorhanden.",
        "running":         "▶ Führe Code aus …",
        "suggestions_for": "📝 Vorschläge für „{}\":",
        "no_suggestions":  "(keine Vorschläge)",
        "ignore":          "🚫 „{}\" ignorieren",
        "connecting":      "Verbinde mit Ollama …",
        "offline":         "Ollama nicht erreichbar",
        "models_found":    "Ollama: {} Modell(e)",
        "no_models":       "(keine Modelle)",
        "no_key":          "Kein API-Key gesetzt!",
        "conn_err":        "Verbindungsfehler",
        "syntax_err":      "Syntaxfehler",
        "runtime_err":     "Laufzeit Fehler",
        "syntax_msg":      "Zeile {}: {}\n\n{}",
        "runtime_msg":     "Details:\n{}",
    },
    "en": {
        "source_label":    "AI Source:",
        "ollama":          "Ollama (Local)",
        "openrouter":      "OpenRouter (Cloud)",
        "not_checked":     "Not checked",
        "workbench":       "Workbench:",
        "spell_active":    "🟢 Spell check active ({})",
        "spell_missing":   "🔴 hunspell not available  →  sudo apt install hunspell-{}",
        "placeholder":     "Describe your part …",
        "btn_generate":    "⚙ Generate Code",
        "btn_apply":       "▶ Apply in FreeCAD",
        "ready":           "Ready.",
        "thinking":        "⏳ AI is thinking …",
        "code_received":   "✅ Code received – please review, then apply.",
        "applied":         "✅ Successfully applied.",
        "no_input":        "⚠ Please enter a description.",
        "no_code":         "⚠ No executable code available.",
        "running":         "▶ Executing code …",
        "suggestions_for": "📝 Suggestions for \"{}\":",
        "no_suggestions":  "(no suggestions)",
        "ignore":          "🚫 ignore \"{}\"",
        "connecting":      "Connecting to Ollama …",
        "offline":         "Ollama not reachable",
        "models_found":    "Ollama: {} model(s)",
        "no_models":       "(no models)",
        "no_key":          "No API key set!",
        "conn_err":        "Connection error",
        "syntax_err":      "Syntax Error",
        "runtime_err":     "Runtime Error",
        "syntax_msg":      "Line {}: {}\n\n{}",
        "runtime_msg":     "Details:\n{}",
    },
    "fr": {
        "source_label":    "Source IA :",
        "ollama":          "Ollama (Local)",
        "openrouter":      "OpenRouter (Cloud)",
        "not_checked":     "Non vérifié",
        "workbench":       "Atelier :",
        "spell_active":    "🟢 Correction active ({})",
        "spell_missing":   "🔴 hunspell non disponible  →  sudo apt install hunspell-{}",
        "placeholder":     "Décrivez votre pièce …",
        "btn_generate":    "⚙ Générer le code",
        "btn_apply":       "▶ Appliquer dans FreeCAD",
        "ready":           "Prêt.",
        "thinking":        "⏳ L'IA réfléchit …",
        "code_received":   "✅ Code reçu – vérifiez, puis appliquez.",
        "applied":         "✅ Appliqué avec succès.",
        "no_input":        "⚠ Veuillez entrer une description.",
        "no_code":         "⚠ Aucun code exécutable disponible.",
        "running":         "▶ Exécution du code …",
        "suggestions_for": "📝 Suggestions pour \"{}\" :",
        "no_suggestions":  "(aucune suggestion)",
        "ignore":          "🚫 ignorer \"{}\"",
        "connecting":      "Connexion à Ollama …",
        "offline":         "Ollama inaccessible",
        "models_found":    "Ollama : {} modèle(s)",
        "no_models":       "(aucun modèle)",
        "no_key":          "Aucune clé API définie !",
        "conn_err":        "Erreur de connexion",
        "syntax_err":      "Erreur de syntaxe",
        "runtime_err":     "Erreur d'exécution",
        "syntax_msg":      "Ligne {} : {}\n\n{}",
        "runtime_msg":     "Détails :\n{}",
    },
    "it": {
        "source_label":    "Sorgente IA:",
        "ollama":          "Ollama (Locale)",
        "openrouter":      "OpenRouter (Cloud)",
        "not_checked":     "Non verificato",
        "workbench":       "Area di lavoro:",
        "spell_active":    "🟢 Controllo ortografico attivo ({})",
        "spell_missing":   "🔴 hunspell non disponibile  →  sudo apt install hunspell-{}",
        "placeholder":     "Descrivi il tuo pezzo …",
        "btn_generate":    "⚙ Genera codice",
        "btn_apply":       "▶ Applica in FreeCAD",
        "ready":           "Pronto.",
        "thinking":        "⏳ L'IA sta pensando …",
        "code_received":   "✅ Codice ricevuto – controlla e poi applica.",
        "applied":         "✅ Applicato con successo.",
        "no_input":        "⚠ Inserisci una descrizione.",
        "no_code":         "⚠ Nessun codice eseguibile.",
        "running":         "▶ Esecuzione del codice …",
        "suggestions_for": "📝 Suggerimenti per \"{}\":",
        "no_suggestions":  "(nessun suggerimento)",
        "ignore":          "🚫 ignora \"{}\"",
        "connecting":      "Connessione a Ollama …",
        "offline":         "Ollama non raggiungibile",
        "models_found":    "Ollama: {} modello/i",
        "no_models":       "(nessun modello)",
        "no_key":          "Nessuna chiave API!",
        "conn_err":        "Errore di connessione",
        "syntax_err":      "Errore di sintassi",
        "runtime_err":     "Errore di runtime",
        "syntax_msg":      "Riga {}: {}\n\n{}",
        "runtime_msg":     "Dettagli:\n{}",
    },
    "es": {
        "source_label":    "Fuente IA:",
        "ollama":          "Ollama (Local)",
        "openrouter":      "OpenRouter (Cloud)",
        "not_checked":     "No comprobado",
        "workbench":       "Área de trabajo:",
        "spell_active":    "🟢 Corrección ortográfica activa ({})",
        "spell_missing":   "🔴 hunspell no disponible  →  sudo apt install hunspell-{}",
        "placeholder":     "Describe tu pieza …",
        "btn_generate":    "⚙ Generar código",
        "btn_apply":       "▶ Aplicar en FreeCAD",
        "ready":           "Listo.",
        "thinking":        "⏳ La IA está pensando …",
        "code_received":   "✅ Código recibido – revisa y luego aplica.",
        "applied":         "✅ Aplicado con éxito.",
        "no_input":        "⚠ Por favor, introduce una descripción.",
        "no_code":         "⚠ No hay código ejecutable.",
        "running":         "▶ Ejecutando código …",
        "suggestions_for": "📝 Sugerencias para \"{}\":",
        "no_suggestions":  "(sin sugerencias)",
        "ignore":          "🚫 ignorar \"{}\"",
        "connecting":      "Conectando a Ollama …",
        "offline":         "Ollama no disponible",
        "models_found":    "Ollama: {} modelo(s)",
        "no_models":       "(sin modelos)",
        "no_key":          "¡No hay clave API!",
        "conn_err":        "Error de conexión",
        "syntax_err":      "Error de sintaxis",
        "runtime_err":     "Error de ejecución",
        "syntax_msg":      "Línea {}: {}\n\n{}",
        "runtime_msg":     "Detalles:\n{}",
    },
}

def t(key: str, *args) -> str:
    """Gibt den übersetzten String zurück, fällt auf Englisch zurück."""
    s = _T.get(LANG, _T["en"]).get(key, _T["en"].get(key, key))
    return s.format(*args) if args else s


# ── Rechtschreibprüfung via hunspell-Subprocess ───────────────────────────────
class HunspellChecker:
    def __init__(self, lang=SPELL_LANG):
        import subprocess, shutil
        if not shutil.which("hunspell"):
            raise RuntimeError("hunspell nicht im PATH")
        self._lang  = lang
        self._cache: dict = {}
        self._proc = subprocess.Popen(
            ["hunspell", "-d", lang, "-a"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, bufsize=1
        )
        self._proc.stdout.readline()

    def check(self, word: str) -> bool:
        if word in self._cache:
            return self._cache[word]
        try:
            self._proc.stdin.write(word + "\n")
            self._proc.stdin.flush()
            line = self._proc.stdout.readline().strip()
            self._proc.stdout.readline()
            ok = line.startswith(("*", "+", "-"))
        except Exception:
            ok = True
        self._cache[word] = ok
        return ok

    def suggest(self, word: str) -> list:
        import subprocess
        try:
            r = subprocess.run(
                ["hunspell", "-d", self._lang],
                input=word, capture_output=True, text=True, timeout=5
            )
            for line in r.stdout.splitlines():
                if ":" not in line:
                    continue
                if line.startswith("&") or line.startswith("#"):
                    return [s.strip() for s in line.split(":",1)[1].split(",") if s.strip()][:7]
        except Exception as e:
            print(f"[Hunspell suggest] {e}")
        return []

    def add_to_session(self, word: str):
        self._cache[word] = True

    def __del__(self):
        try: self._proc.terminate()
        except Exception: pass


try:
    _DICT = HunspellChecker(SPELL_LANG)
except Exception:
    _DICT = None


# ── Spell-Highlighter ─────────────────────────────────────────────────────────
class SpellHighlighter(QtGui.QSyntaxHighlighter):
    WORD_RE = re.compile(r'\b[A-Za-zÀ-ÖØ-öø-ÿ]{3,}\b')

    def __init__(self, document):
        super().__init__(document)
        self._fmt = QtGui.QTextCharFormat()
        self._fmt.setBackground(QtGui.QColor("#6b1a1a"))
        self._fmt.setForeground(QtGui.QColor("#ff6b6b"))

    def highlightBlock(self, text):
        if _DICT is None:
            return
        for m in self.WORD_RE.finditer(text):
            word = m.group()
            if word[0].isupper() and len(word) > 1 and word[1].isupper():
                continue
            try:
                if not _DICT.check(word):
                    self.setFormat(m.start(), len(word), self._fmt)
            except Exception:
                pass


# ── SpellTextEdit ─────────────────────────────────────────────────────────────
class SpellTextEdit(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._highlighter = SpellHighlighter(self.document())

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        if _DICT is not None:
            cursor = self.cursorForPosition(event.pos())
            cursor.select(QtGui.QTextCursor.WordUnderCursor)
            word = re.sub(r"[^\w\u00C0-\u024F]", "", cursor.selectedText())
            if word and len(word) >= 3:
                is_wrong = not _DICT.check(word)
                if is_wrong:
                    suggestions = _DICT.suggest(word)
                    QAction = getattr(QtGui, 'QAction', None) or QtWidgets.QAction
                    first = menu.actions()[0] if menu.actions() else None
                    menu.insertSeparator(first)
                    title = QAction(t("suggestions_for", word), menu)
                    title.setEnabled(False)
                    menu.insertAction(first, title)
                    menu.insertSeparator(first)
                    if suggestions:
                        for s in suggestions:
                            act = QAction(f"✔ {s}", menu)
                            def make_replacer(repl, c=QtGui.QTextCursor(cursor)):
                                def do():
                                    c.insertText(repl)
                                    self._highlighter.rehighlight()
                                return do
                            act.triggered.connect(make_replacer(s))
                            menu.insertAction(first, act)
                    else:
                        na = QAction(t("no_suggestions"), menu)
                        na.setEnabled(False)
                        menu.insertAction(first, na)
                    menu.insertSeparator(first)
                    ign = QAction(t("ignore", word), menu)
                    ign.triggered.connect(lambda _, w=word: self._ignore_word(w))
                    menu.insertAction(first, ign)
                    menu.insertSeparator(first)
        menu.exec(event.globalPos())

    def _ignore_word(self, word):
        try:
            _DICT.add_to_session(word)
            self._highlighter.rehighlight()
        except Exception:
            pass


# ── Syntax-Highlighter (Code-Anzeige) ────────────────────────────────────────
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
        "You are a FreeCAD 1.1.1 Python expert. "
        "Reply ONLY with pure Python code, NO explanations, NO markdown fences.\n\n"
        "MANDATORY RULES:\n"
        "- Boolean ops ONLY like this:\n"
        "    result = a.cut(b)   # subtraction\n"
        "    result = a.fuse(b)  # union\n"
        "- NEVER use -= or += on Part objects\n"
        "- After every boolean op write the result into the document:\n"
        "    obj = doc.addObject('Part::Feature', 'Name')\n"
        "    obj.Shape = result\n"
        "- Dimensions always as float: 40.0 not 40mm\n"
        "- No .Support, no saveCopy, no export\n\n"
        "EXAMPLE – 40mm cube with 10mm diameter hole:\n"
        "import Part\n"
        "cube     = Part.makeBox(40.0, 40.0, 40.0)\n"
        "cyl      = Part.makeCylinder(5.0, 40.0, App.Vector(20.0,20.0,0.0), App.Vector(0,0,1))\n"
        "result   = cube.cut(cyl)\n"
        "obj = doc.addObject('Part::Feature', 'CubeWithHole')\n"
        "obj.Shape = result\n"
        "doc.recompute()\n"
        f"\nThe user writes in language code: '{LANG}'. "
        "Understand the description regardless of language, but always output only Python code.\n"
    )

    def __init__(self):
        super().__init__()
        self.openrouter_key = "DEIN_KEY_HIER"
        self.worker = None
        self._build_ui()
        self._refresh_models()

    def _build_ui(self):
        g = QtWidgets.QGridLayout(self)
        g.setSpacing(6)
        g.setContentsMargins(8, 8, 8, 8)

        g.addWidget(QtWidgets.QLabel(t("source_label")), 0, 0, 1, 2)
        self.source_box = QtWidgets.QComboBox()
        self.source_box.addItems([t("ollama"), t("openrouter")])
        self.source_box.currentIndexChanged.connect(self._refresh_models)
        g.addWidget(self.source_box, 1, 0, 1, 2)

        self.model_box = QtWidgets.QComboBox()
        g.addWidget(self.model_box, 2, 0)
        btn_ref = QtWidgets.QPushButton("🔄")
        btn_ref.setFixedWidth(35)
        btn_ref.clicked.connect(self._refresh_models)
        g.addWidget(btn_ref, 2, 1)

        row_conn = QtWidgets.QHBoxLayout()
        self.conn_dot  = QtWidgets.QLabel("●")
        self.conn_dot.setFixedWidth(18)
        self.conn_info = QtWidgets.QLabel(t("not_checked"))
        self.conn_info.setStyleSheet("color:gray; font-size:11px;")
        row_conn.addWidget(self.conn_dot)
        row_conn.addWidget(self.conn_info)
        row_conn.addStretch()
        g.addLayout(row_conn, 3, 0, 1, 2)

        wb_row = QtWidgets.QHBoxLayout()
        wb_row.addWidget(QtWidgets.QLabel(t("workbench")))
        self.wb_label = QtWidgets.QLabel("…")
        self.wb_label.setStyleSheet("color:#dcdcaa; font-weight:bold; font-size:11px;")
        wb_row.addWidget(self.wb_label)
        wb_row.addStretch()
        g.addLayout(wb_row, 4, 0, 1, 2)

        spell_txt = t("spell_active", SPELL_LANG) if _DICT else t("spell_missing", SPELL_LANG)
        spell_lbl = QtWidgets.QLabel(spell_txt)
        spell_lbl.setStyleSheet("font-size:10px; color:gray;")
        g.addWidget(spell_lbl, 5, 0, 1, 2)

        self.input_text = SpellTextEdit()
        self.input_text.setStyleSheet(
            "background-color:#2b2b2b; color:#f0f0f0; font-size:12px;")
        self.input_text.setPlaceholderText(t("placeholder"))
        self.input_text.setFixedHeight(90)
        g.addWidget(self.input_text, 6, 0, 1, 2)

        self.btn_ask = QtWidgets.QPushButton(t("btn_generate"))
        self.btn_ask.setStyleSheet(
            "background-color:#444;color:white;padding:8px;font-weight:bold;")
        self.btn_ask.clicked.connect(self._handle_request)
        g.addWidget(self.btn_ask, 7, 0, 1, 2)

        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        self.progress.setVisible(False)
        g.addWidget(self.progress, 8, 0, 1, 2)

        self.status_lbl = QtWidgets.QLabel(t("ready"))
        self.status_lbl.setStyleSheet("color:gray; font-size:11px; padding:2px 0;")
        g.addWidget(self.status_lbl, 9, 0, 1, 2)

        self.code_display = QtWidgets.QPlainTextEdit()
        self.code_display.setStyleSheet(
            "background-color:#1e1e1e; color:#a9b7c6; "
            "font-family:'Monospace'; font-size:12px;")
        PythonHighlighter(self.code_display.document())
        g.addWidget(self.code_display, 10, 0, 1, 2)
        g.setRowStretch(10, 1)

        self.btn_run = QtWidgets.QPushButton(t("btn_apply"))
        self.btn_run.setFixedHeight(40)
        self.btn_run.setStyleSheet(
            "background-color:#2e7d32;color:white;font-weight:bold;")
        self.btn_run.clicked.connect(self._execute_code)
        g.addWidget(self.btn_run, 11, 0, 1, 2)

    def _set_conn(self, ok, text):
        color = "#4caf50" if ok else "#f44336"
        self.conn_dot.setStyleSheet(f"color:{color}; font-size:14px;")
        self.conn_info.setText(text)
        self.conn_info.setStyleSheet(f"color:{color}; font-size:11px;")

    def _set_busy(self, busy, msg=""):
        self.progress.setVisible(busy)
        self.btn_ask.setEnabled(not busy)
        self.btn_run.setEnabled(not busy)
        self.status_lbl.setText(msg if msg else (t("ready") if not busy else ""))
        QtWidgets.QApplication.processEvents()

    def _refresh_models(self):
        import requests
        self.model_box.clear()
        if t("ollama") in self.source_box.currentText():
            self._set_conn(False, t("connecting"))
            QtWidgets.QApplication.processEvents()
            try:
                r = requests.get("http://localhost:11434/api/tags", timeout=3)
                models = [m["name"] for m in r.json().get("models", [])]
                self.model_box.addItems(models or [t("no_models")])
                self._set_conn(bool(models), t("models_found", len(models)))
            except requests.exceptions.ConnectionError:
                self.model_box.addItem(t("offline"))
                self._set_conn(False, t("offline"))
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
                self._set_conn(False, t("no_key"))
            else:
                try:
                    r = requests.get(
                        "https://openrouter.ai/api/v1/auth/key",
                        headers={"Authorization": f"Bearer {self.openrouter_key}"},
                        timeout=5)
                    if r.status_code == 200:
                        credits = r.json().get("data", {}).get("limit_remaining", "?")
                        self._set_conn(True, f"OpenRouter OK | {credits}")
                    else:
                        self._set_conn(False, f"OpenRouter {r.status_code}")
                except Exception as e:
                    self._set_conn(False, f"{t('conn_err')}: {e}")

    def _build_system_prompt(self):
        try:
            wb_name = Gui.activeWorkbench().__class__.__name__
        except Exception:
            wb_name = "Unknown"
        labels = {
            "PartDesignWorkbench": "Part Design",
            "PartWorkbench": "Part",
            "MeshWorkbench": "Mesh",
        }
        self.wb_label.setText(labels.get(wb_name, wb_name))
        wb_hints = {
            "PartDesignWorkbench": (
                "Active workbench: PART DESIGN.\n"
                "MANDATORY: Always Body → Sketch → Pad/Pocket. NEVER Part.makeBox!\n"
            ),
            "PartWorkbench": (
                "Active workbench: PART.\n"
                "Use Part primitives and boolean ops: makeBox/makeCylinder/makeSphere, cut()/fuse().\n"
            ),
            "MeshWorkbench": (
                "Active workbench: MESH. Use import Mesh.\n"
            ),
        }
        wb_hint = wb_hints.get(wb_name, f"Active workbench: {wb_name}.\n")
        return self.SYSTEM_PROMPT + wb_hint

    def _handle_request(self):
        prompt = self.input_text.toPlainText().strip()
        if not prompt:
            self.status_lbl.setText(t("no_input"))
            return
        self._set_busy(True, t("thinking"))
        source = self.source_box.currentText()
        model  = self.model_box.currentText()
        self.worker = QtCore.QThread()
        self._task = _APIWorker(source, model, prompt, self.openrouter_key,
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
        self._set_busy(False, t("code_received"))

    def _on_error(self, msg):
        self.code_display.setPlainText(f"# Error:\n# {msg}")
        self._set_busy(False, f"❌ {msg}")
        self._set_conn(False, t("conn_err"))

    def _clean(self, code: str) -> str:
        code = re.sub(r'```[\w]*', '', code).strip()
        result = []
        for line in code.splitlines():
            s = line.strip()
            if not s:
                result.append(''); continue
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
        code = re.sub(r'^(\s*)(\w+)\s*-=\s*(.+)$', r'\1\2 = \2.cut(\3)',   flags=re.MULTILINE, string=code)
        code = re.sub(r'^(\s*)(\w+)\s*\+=\s*(.+)$', r'\1\2 = \2.fuse(\3)', flags=re.MULTILINE, string=code)
        code = re.sub(r'^(\s*)(\w+)\s*\*=\s*(.+)$', r'\1\2 = \2.common(\3)', flags=re.MULTILINE, string=code)
        return code

    def _execute_code(self):
        code = self._clean(self.code_display.toPlainText())
        if not code or code.startswith("#"):
            self.status_lbl.setText(t("no_code")); return
        if App.ActiveDocument is None:
            App.newDocument("AI_Part")
        self._set_busy(True, t("running"))
        try:
            import Part, Sketcher, math
            ns = {"App": App, "Gui": Gui, "Part": Part, "Sketcher": Sketcher,
                  "math": math, "doc": App.ActiveDocument,
                  "Vector": App.Vector, "Placement": App.Placement, "Rotation": App.Rotation}
            exec(compile(code, "<AI-Code>", "exec"), ns)
            App.ActiveDocument.recompute()
            Gui.updateGui()
            Gui.SendMsgToActiveView("ViewFit")
            self._set_busy(False, t("applied"))
        except SyntaxError as e:
            self._set_busy(False, f"❌ {t('syntax_err')} {e.lineno}: {e.msg}")
            QtWidgets.QMessageBox.critical(None, t("syntax_err"),
                t("syntax_msg", e.lineno, e.msg, e.text))
        except Exception as e:
            self._set_busy(False, f"❌ {t('runtime_err')}: {e}")
            QtWidgets.QMessageBox.critical(None, t("runtime_err"),
                t("runtime_msg", str(e)))


# ── Worker-Thread ────────────────────────────────────────────────────────────
class _APIWorker(QtCore.QObject):
    done  = QtCore.Signal(str)
    error = QtCore.Signal(str)

    def __init__(self, source, model, prompt, key, system):
        super().__init__()
        self.source = source; self.model = model
        self.prompt = prompt; self.key = key; self.system = system

    def run(self):
        import requests
        try:
            if t("ollama") in self.source:
                r = requests.post(
                    "http://localhost:11434/api/generate",
                    json={"model": self.model,
                          "prompt": f"{self.system}\n\nTask: {self.prompt}",
                          "stream": False}, timeout=600)
                r.raise_for_status()
                self.done.emit(r.json().get("response", ""))
            else:
                r = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.key}",
                             "Content-Type": "application/json"},
                    json={"model": self.model,
                          "messages": [{"role": "system", "content": self.system},
                                       {"role": "user",   "content": self.prompt}]},
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
    panel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    dock = QtWidgets.QDockWidget("KI Multi-Source Assistent")
    dock.setWidget(panel)
    dock.setMinimumWidth(200)
    dock.setMaximumWidth(16777215)
    dock.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    mw.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

if __name__ == "__main__":
    add_ai_panel()
